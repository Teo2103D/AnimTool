import maya.cmds as cmds

#By Teo2103D

def create_group_based_on_selection():
    # List of words for each category
    arm_list = ["wrist", "hand", "elbow", "arm", "shoulder", "clavicle"]
    leg_list = ["hip", "pelvis", "femur", "kneecap", "knee", "leg", "ankle", "foot", "tibia"]

    # Get the selected objects
    selected_objects = cmds.ls(selection=True)
    
    # Check if any objects are selected
    if len(selected_objects) == 0:
        cmds.error("Please select at least one object.")
        return

    # Function to check if a word from a list is present in the object name
    def contains_word(obj_name, word_list):
        for word in word_list:
            if word.lower() in obj_name.lower():  # Check case-insensitively
                return True
        return False

    # Function to determine if the object is IK or FK
    def detect_ik_fk(obj_name):
        if "ik" in obj_name.lower():
            return "FK"  # Locator will be FK for IK objects
        elif "fk" in obj_name.lower():
            return "IK"  # Locator will be IK for FK objects
        else:
            return None

    # Determine the group type and category
    is_arm = None
    is_leg = None
    group_type = None  # IK or FK

    for obj in selected_objects:
        if contains_word(obj, arm_list):
            if is_arm is None:
                is_arm = True
            elif is_leg:
                cmds.error("The selection contains objects from both 'arm' and 'leg' groups.")
                return
        elif contains_word(obj, leg_list):
            if is_leg is None:
                is_leg = True
            elif is_arm:
                cmds.error("The selection contains objects from both 'arm' and 'leg' groups.")
                return
        else:
            cmds.error(f"The object '{obj}' does not belong to any valid group ('arm' or 'leg').")
            return

        # Detect if the object is IK or FK
        detected_type = detect_ik_fk(obj)
        if detected_type:
            if group_type is None:
                group_type = detected_type
            elif group_type != detected_type:
                cmds.error("The selection contains objects from both 'IK' and 'FK' groups.")
                return

    # Create the locators
    create_locators_with_hierarchy_based_names(selected_objects, is_arm, is_leg, group_type)

def get_top_parent(obj):
    """
    Finds the topmost parent in the hierarchy for the given object.
    """
    parent = cmds.listRelatives(obj, parent=True, fullPath=True)
    while parent:
        obj = parent[0]
        parent = cmds.listRelatives(obj, parent=True, fullPath=True)
    return obj.split('|')[-1]  # Return the name of the top-level parent

def create_locators_with_hierarchy_based_names(selected_objects, is_arm, is_leg, group_type):
    counters = {'_L': 0, '_R': 0, '': 0}
    prefix = "Arm_" if is_arm else "Leg_"

    for selected_object in selected_objects:
        # Detect the suffix (_L, _R, or none)
        if selected_object.endswith("_L"):
            suffix = "_L"
        elif selected_object.endswith("_R"):
            suffix = "_R"
        else:
            suffix = ""

        # Increment the corresponding counter
        counters[suffix] += 1

        # Get the top parent name for the selected object
        top_parent_name = get_top_parent(selected_object)

        # Determine the locator type based on the object type (IK/FK)
        locator_type = group_type  # This is "FK" or "IK" based on the detected type

        # Construct the locator name
        locator_name = f"{prefix}{locator_type}_{top_parent_name}_{counters[suffix]}_loc{suffix}"

        # Create the locator
        locator = cmds.spaceLocator(name=locator_name)[0]

        # Match the transform of the locator to the selected object
        cmds.matchTransform(locator, selected_object, position=True, rotation=True, scale=True)

        # Add a parentConstraint to the locator
        cmds.parentConstraint(selected_object, locator, maintainOffset=False)

        # Print message for the created locator
        print(f"Locator '{locator_name}' created and aligned with '{selected_object}'.")

# Execute the function
create_group_based_on_selection()

#By Teo2103D
