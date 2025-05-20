import maya.cmds as cmds

#By Teo2103D

def create_three_groups_with_constraints_and_prefix():
    # List of keywords for arms and legs
    arm_list = ["wrist", "hand", "elbow", "arm", "shoulder", "clavicle"]
    leg_list = ["hip", "pelvis", "femur", "kneecap", "knee", "leg", "ankle", "foot", "tibia"]

    # Selection check
    selection = cmds.ls(selection=True)
    if len(selection) != 3:
        cmds.error("Please select exactly three objects.")
        return

    # Helper to check if object name contains any word from a list
    def contains_word(obj_name, word_list):
        return any(word.lower() in obj_name.lower() for word in word_list)

    # Helper to get the topmost parent in the hierarchy
    def get_top_parent(obj):
        parent = cmds.listRelatives(obj, parent=True, fullPath=True)
        while parent:
            obj = parent[0]
            parent = cmds.listRelatives(obj, parent=True, fullPath=True)
        return obj.split('|')[-1]  # Only the name

    # Verify if all objects are in the same hierarchy
    top_parents = {get_top_parent(obj) for obj in selection}
    if len(top_parents) > 1:
        cmds.error("All selected objects must be in the same hierarchy.")
        return

    # Get the top parent name (used in naming)
    hierarchy_name = list(top_parents)[0]

    # Detect the group (arm or leg)
    is_arm = all(contains_word(obj, arm_list) for obj in selection)
    is_leg = all(contains_word(obj, leg_list) for obj in selection)

    if is_arm and is_leg:
        cmds.error("The selection contains objects from both 'arm' and 'leg' groups.")
        return
    elif not is_arm and not is_leg:
        cmds.error("The selection does not match any valid group ('arm' or 'leg').")
        return

    # Define the prefix
    prefix = "Arm_" if is_arm else "Leg_"

    # Helper to get all parents of an object
    def get_all_parents(obj):
        parents = []
        current_parent = cmds.listRelatives(obj, parent=True, fullPath=True)
        while current_parent:
            parents.append(current_parent[0])
            current_parent = cmds.listRelatives(current_parent[0], parent=True, fullPath=True)
        return parents

    # Helper to determine the suffix (_L, _R, or none)
    def get_suffix(obj_name):
        if obj_name.endswith('_L'):
            return '_L'
        elif obj_name.endswith('_R'):
            return '_R'
        else:
            return ''

    # Dictionary to store parent-child relationships
    hierarchy = {}

    # Fill the dictionary with hierarchical levels
    for obj in selection:
        parents = get_all_parents(obj)
        hierarchy[obj] = len(parents)

    # Sort objects by their hierarchical level (less parents = higher in hierarchy)
    sorted_hierarchy = sorted(hierarchy.items(), key=lambda x: x[1])

    # Extract the sorted objects
    top_object = sorted_hierarchy[0][0]
    middle_object = sorted_hierarchy[1][0]
    bottom_object = sorted_hierarchy[2][0]

    # Determine the suffix based on the selected objects
    suffixes = [get_suffix(obj) for obj in selection]
    unique_suffixes = list(set(suffixes) - {''})  # Filter out empty suffixes

    # If there are multiple suffixes (_L and _R), display an error
    if len(unique_suffixes) > 1:
        cmds.error("The selected objects must not contain both '_L' and '_R' suffixes.")
        return

    # Use the first valid suffix or none
    suffix = unique_suffixes[0] if unique_suffixes else ''

    # Create the first group
    group_top_name = f"{prefix}IK_PV_constraint_grp{suffix}"
    group_top = cmds.group(em=True, name=group_top_name)
    cmds.pointConstraint(top_object, group_top, maintainOffset=False)
    cmds.pointConstraint(middle_object, group_top, maintainOffset=False)

    # Create the second group
    group_bottom_name = f"{prefix}IK_PV_constraint_C_grp{suffix}"
    group_bottom = cmds.group(em=True, name=group_bottom_name)
    cmds.pointConstraint(middle_object, group_bottom, maintainOffset=False)
    cmds.pointConstraint(bottom_object, group_bottom, maintainOffset=False)

    # Create the third group
    group_combined_name = f"{prefix}IK_PV_constraint_B_grp{suffix}"
    group_combined = cmds.group(em=True, name=group_combined_name)
    cmds.pointConstraint(group_top, group_combined, maintainOffset=False)
    cmds.pointConstraint(group_bottom, group_combined, maintainOffset=False)

    # Add an aim constraint for the middle object on the third group
    cmds.aimConstraint(
        middle_object, group_combined, maintainOffset=False,
        aimVector=(1, 0, 0), upVector=(0, 1, 0), worldUpType="vector", worldUpVector=(0, 1, 0)
    )

    # Create a locator with a MAT on the "IK_PV_constraint_B_grp" group
    locator_name = f"{prefix}IK_PV_{hierarchy_name}_loc{suffix}"
    locator = cmds.spaceLocator(name=locator_name)[0]
    cmds.matchTransform(locator, group_combined, position=True, rotation=True, scale=False)

    # Reset the rotation of the locator
    cmds.setAttr(f"{locator}.rotateX", 0)
    cmds.setAttr(f"{locator}.rotateY", 0)
    cmds.setAttr(f"{locator}.rotateZ", 0)

    # Create an offset group for the locator
    offset_group_name = f"{prefix}IK_PV_{hierarchy_name}_loc_offset{suffix}"
    offset_group = cmds.group(em=True, name=offset_group_name)

    # Create a second offset group (offsetV2) to hold the offset group
    offsetV2_group_name = f"{prefix}IK_PV_{hierarchy_name}_loc_offsetV2{suffix}"
    offsetV2_group = cmds.group(em=True, name=offsetV2_group_name)

    # Parent the locator to the offset group
    cmds.parent(locator, offset_group)
    cmds.parent(offset_group, offsetV2_group)

    # Apply MAT of the offsetV2 group to the "IK_PV_constraint_B_grp" group
    cmds.matchTransform(offsetV2_group, group_combined, position=True, rotation=True, scale=False)

    # Apply -90° Y rotation and 42.5 units X translation **to the offset group**
    cmds.setAttr(f"{offset_group}.rotateY", -90)
    cmds.setAttr(f"{offset_group}.translateX", 42.5)

    # Reset the locator's translation
    cmds.setAttr(f"{locator}.translateX", 0)
    cmds.setAttr(f"{locator}.translateY", 0)
    cmds.setAttr(f"{locator}.translateZ", 0)

    # Apply a parent constraint from the "IK_PV_constraint_B_grp" group to the offsetV2 group
    cmds.parentConstraint(group_combined, offsetV2_group, maintainOffset=True)

# Execute the function
create_three_groups_with_constraints_and_prefix()

#By Teo2103D
