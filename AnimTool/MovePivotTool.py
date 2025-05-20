import maya.cmds as cmds

#By Teo2103D

# Store objects that already have locators
tracked_objects = {}

def neutralize_pivot_effect(obj):
    """
    Finds all parent and point constraints that use the selected object as a target,
    then connects a Multiply Divide Node and a single PlusMinusAverage Node to correct the offsets without creating a cycle.
    """
    if not cmds.objExists(obj):
        cmds.warning(f"The object {obj} does not exist!")
        return

    # Find all parent and point constraints in the scene
    all_parent_constraints = cmds.ls(type="parentConstraint") or []
    all_point_constraints = cmds.ls(type="pointConstraint") or []
    
    relevant_constraints = []

    # Check if the object is a target of parentConstraints
    for constraint in all_parent_constraints:
        targets = cmds.parentConstraint(constraint, q=True, tl=True)
        if obj in targets:
            relevant_constraints.append(constraint)

    # Check if the object is a target of pointConstraints
    for constraint in all_point_constraints:
        targets = cmds.pointConstraint(constraint, q=True, tl=True)
        if obj in targets:
            relevant_constraints.append(constraint)

    if not relevant_constraints:
        cmds.warning(f"No parent or point constraint affecting {obj} found.")
        return

    # Create a Multiply Divide Node to reverse the Scale Pivot
    mult_node = f"{obj}_multReversePivot"
    if not cmds.objExists(mult_node):
        mult_node = cmds.createNode("multiplyDivide", name=mult_node)
        cmds.setAttr(f"{mult_node}.operation", 1)  # Multiplication
        cmds.setAttr(f"{mult_node}.input2X", -1)
        cmds.setAttr(f"{mult_node}.input2Y", -1)
        cmds.setAttr(f"{mult_node}.input2Z", -1)

    # Connect the object's Scale Pivot to the Multiply Divide Node
    cmds.connectAttr(f"{obj}.scalePivotX", f"{mult_node}.input1X", force=True)
    cmds.connectAttr(f"{obj}.scalePivotY", f"{mult_node}.input1Y", force=True)
    cmds.connectAttr(f"{obj}.scalePivotZ", f"{mult_node}.input1Z", force=True)

    # Apply the connection to the found constraints
    for constraint in relevant_constraints:
        # Determine if it's a parentConstraint or a pointConstraint
        is_parent_constraint = cmds.objectType(constraint) == "parentConstraint"

        # Get the offsets before the connection
        if is_parent_constraint:
            offset_x = cmds.getAttr(f"{constraint}.target[0].targetOffsetTranslateX")
            offset_y = cmds.getAttr(f"{constraint}.target[0].targetOffsetTranslateY")
            offset_z = cmds.getAttr(f"{constraint}.target[0].targetOffsetTranslateZ")
        else:
            offset_x = cmds.getAttr(f"{constraint}.offsetX")
            offset_y = cmds.getAttr(f"{constraint}.offsetY")
            offset_z = cmds.getAttr(f"{constraint}.offsetZ")

        # Create a single PlusMinusAverage Node per constraint
        add_node = cmds.createNode("plusMinusAverage", name=f"{constraint}_addOffset")
        cmds.setAttr(f"{add_node}.operation", 1)  # Addition mode

        # Set the current offset values in the Add nodes
        cmds.setAttr(f"{add_node}.input1D[1]", offset_x)  # X → input1D
        cmds.setAttr(f"{add_node}.input2D[1].input2Dx", offset_y)  # Y → input2Dx
        cmds.setAttr(f"{add_node}.input3D[1].input3Dx", offset_z)  # Z → input3Dx

        # Connect the Multiply Divide Node to the Add Node for each axis
        cmds.connectAttr(f"{mult_node}.outputX", f"{add_node}.input1D[0]", force=True)  # X
        cmds.connectAttr(f"{mult_node}.outputY", f"{add_node}.input2D[0].input2Dx", force=True)  # Y
        cmds.connectAttr(f"{mult_node}.outputZ", f"{add_node}.input3D[0].input3Dx", force=True)  # Z

        # Connect the Add Nodes to the offsets of the respective constraints
        if is_parent_constraint:
            cmds.connectAttr(f"{add_node}.output1D", f"{constraint}.target[0].targetOffsetTranslateX", force=True)
            cmds.connectAttr(f"{add_node}.output2D.output2Dx", f"{constraint}.target[0].targetOffsetTranslateY", force=True)
            cmds.connectAttr(f"{add_node}.output3D.output3Dx", f"{constraint}.target[0].targetOffsetTranslateZ", force=True)
        else:
            cmds.connectAttr(f"{add_node}.output1D", f"{constraint}.offsetX", force=True)
            cmds.connectAttr(f"{add_node}.output2D.output2Dx", f"{constraint}.offsetY", force=True)
            cmds.connectAttr(f"{add_node}.output3D.output3Dx", f"{constraint}.offsetZ", force=True)

    print(f" Pivot of {obj} neutralized on its parent and point constraints with a single PlusMinusAverage per constraint.")

def create_locators_for_object(obj):
    """
    Creates three locators (Origin, PosPivot1, PosPivot2) in the correct order:
    - Creating the locator
    - Parenting the locator to the selected object
    - Snapping to the object's world space
    - Setting the locator's translation and rotation values to 0
    """
    if obj in tracked_objects:
        return tracked_objects[obj]  # Return existing locators

    locators = {}
    locator_names = ["Origin", "PosPivot1", "PosPivot2"]

    # Get the world space position of the object
    obj_world_pos = cmds.xform(obj, q=True, ws=True, rp=True)

    for loc_name in locator_names:
        full_name = f"{loc_name}_{obj}"

        if cmds.objExists(full_name):
            locators[loc_name] = full_name
        else:
            loc = cmds.spaceLocator(name=full_name)[0]

            # Parent the locator to the selected object
            cmds.parent(loc, obj)

            # Snap the locator to the object's world space position
            cmds.xform(loc, ws=True, t=obj_world_pos)

            # Reset translation and rotation to 0 without freezing
            cmds.setAttr(f"{loc}.translate", 0, 0, 0)
            cmds.setAttr(f"{loc}.rotate", 0, 0, 0)

            # Set the scale values to 1
            cmds.setAttr(f"{loc}.scale", 1, 1, 1)

            locators[loc_name] = loc

            # Make "Origin" invisible
            if loc_name == "Origin":
                cmds.setAttr(f"{loc}.visibility", 0)

            # Change the color of PosPivot1 and PosPivot2
            if loc_name == "PosPivot1":
                cmds.setAttr(f"{loc}.overrideEnabled", 1)
                cmds.setAttr(f"{loc}.overrideColor", 17)  # Yellow

            if loc_name == "PosPivot2":
                cmds.setAttr(f"{loc}.overrideEnabled", 1)
                cmds.setAttr(f"{loc}.overrideColor", 16)  # White

    tracked_objects[obj] = locators  # Store locators for this object
    return locators

def create_gizmo_curve(obj):
    """
    Creates a cross-shaped gizmo with a sphere that follows the pivot of the object.
    - The gizmo is first parented to the object.
    - It is then aligned to the pivot in world space.
    - Finally, it is reset in translation, rotation, and scale before being constrained.
    """

    # Delete the old gizmo if it exists
    gizmo_name = f"gizmoCurve_{obj}"
    if cmds.objExists(gizmo_name):
        cmds.delete(gizmo_name)

    # Create axis segments as curves
    axis_curves = []
    axis_points = [
        [(0, 0, 0), (2, 0, 0)],  # X
        [(0, 0, 0), (0, 2, 0)],  # Y
        [(0, 0, 0), (0, 0, 2)],  # Z
    ]
    
    for points in axis_points:
        curve = cmds.curve(d=1, p=points, k=[0, 1])
        axis_curves.append(curve)

    # Create spheres as curves
    sphere1 = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), r=1.5, sections=20)[0]
    sphere2 = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), r=1.5, sections=20)[0]
    sphere3 = cmds.circle(nr=(0, 0, 1), c=(0, 0, 0), r=1.5, sections=20)[0]

    # Create the gizmo group
    gizmo_curve_group = cmds.group(empty=True, name=gizmo_name)

    # Parent the curves directly under the group
    for curve in axis_curves + [sphere1, sphere2, sphere3]:
        cmds.parent(curve, gizmo_curve_group)

    # Enable "reference" display to avoid accidental selection
    for curve in axis_curves + [sphere1, sphere2, sphere3]:
        cmds.setAttr(f"{curve}.overrideEnabled", 1)
        cmds.setAttr(f"{curve}.overrideDisplayType", 2)

    # **1. Parent the gizmo group to the object BEFORE any transformation**
    cmds.parent(gizmo_curve_group, obj)

    # **2. Snap to the world pivot**
    pivot_position = cmds.xform(obj, query=True, worldSpace=True, rp=True)
    cmds.xform(gizmo_curve_group, worldSpace=True, translation=pivot_position)

    # **3. Reset values (keep the correct alignment)**
    cmds.setAttr(f"{gizmo_curve_group}.translate", 0, 0, 0)
    cmds.setAttr(f"{gizmo_curve_group}.rotate", 0, 0, 0)
    cmds.setAttr(f"{gizmo_curve_group}.scale", 0.25, 0.25, 0.25)

    # **4. Constraints to follow the object**
    cmds.orientConstraint(obj, gizmo_curve_group, maintainOffset=True)
    cmds.pointConstraint(obj, gizmo_curve_group, maintainOffset=True)

    print(f"\u2705 Gizmo Curve for {obj} created properly with reset and constraints.")

def unlock_pivot_attributes():
    # Récupérer les objets sélectionnés
    selected_objects = cmds.ls(selection=True)
    
    if not selected_objects:
        cmds.warning("Aucun objet sélectionné.")
        return

    # Liste des attributs pivots à vérifier et déverrouiller
    pivot_attributes = [
        "rotatePivotX", "rotatePivotY", "rotatePivotZ", 
        "scalePivotX", "scalePivotY", "scalePivotZ", 
        "scalePivotTranslateX", "scalePivotTranslateY", "scalePivotTranslateZ", 
        "rotatePivotTranslateX", "rotatePivotTranslateY", "rotatePivotTranslateZ"
    ]
    
    # Parcourir les objets sélectionnés
    for obj in selected_objects:
        # Vérifier si l'objet est référencé
        is_reference = cmds.referenceQuery(obj, isNodeReferenced=True)
        
        # Si l'objet est référencé, afficher un message
        if is_reference:
            cmds.warning(f"L'objet {obj} est référencé. Tentative de déverrouillage des pivots...")
        
        # Vérifier et déverrouiller les attributs des pivots
        for attr in pivot_attributes:
            if cmds.attributeQuery(attr, node=obj, exists=True):
                if cmds.getAttr(f"{obj}.{attr}", lock=True):
                    try:
                        # Déverrouiller l'attribut
                        cmds.setAttr(f"{obj}.{attr}", lock=False)
                        print(f"Attribut {attr} de {obj} déverrouillé.")
                    except Exception as e:
                        print(f"Impossible de déverrouiller l'attribut {attr} de {obj}: {e}")
                else:
                    print(f"L'attribut {attr} de {obj} n'est pas verrouillé.")
            else:
                print(f"L'attribut {attr} n'existe pas sur {obj}.")
                
def snap_pivot_to_locator(obj, locator):
    """
    Snaps the object's pivot to the position of the given locator (rotationPivot and scalePivot),
    and adds keyframes for all pivot attributes of the object at the current frame.
    """
    
    # Check if the object is selected
    selected = cmds.ls(selection=True)
    if obj not in selected:
        cmds.warning(f" You must select {obj} before modifying its pivot.")
        return
        
        
    # Get the position of the locator in world space
    locator_pos = cmds.xform(locator, q=True, ws=True, t=True)

    # Get the current frame to add a keyframe
    current_frame = cmds.currentTime(query=True)

    # Move the pivots of the object without moving the object itself
    cmds.xform(obj, ws=True, rp=locator_pos)  # Rotation pivot
    cmds.xform(obj, ws=True, sp=locator_pos)  # Scale pivot

    # Add keyframes for all pivot and transform attributes
    # Keyframe for rotationPivot (rp) and scalePivot (sp)
    cmds.setKeyframe(obj, attribute="rotatePivot", t=current_frame)
    cmds.setKeyframe(obj, attribute="scalePivot", t=current_frame)
    
    # Keyframe for translation and rotation of the pivots (even if the values are 0)
    cmds.setKeyframe(obj, attribute="rotatePivotTranslate", t=current_frame)
    cmds.setKeyframe(obj, attribute="scalePivotTranslate", t=current_frame)

    # Keyframe for translation and rotation of the object itself (just in case)
    cmds.setKeyframe(obj, attribute="translate", t=current_frame)
    cmds.setKeyframe(obj, attribute="rotate", t=current_frame)

    print(f" The rotation and scale pivots of {obj} have been snapped to {locator}, and animation keys have been added.")

def create_locators_and_gizmo_for_selected_object():
    """
    Creates locators and gizmo for the selected object and refreshes the UI.
    """
    selected = cmds.ls(selection=True)
    if not selected:
        cmds.warning("Please select an object before creating locators and a gizmo.")
        return

    obj = selected[0]
    
    # Check unlock pivot object
    unlock_pivot_attributes()

    # Create the offsets for the object
    neutralize_pivot_effect(obj)

    # Create locators for the object
    create_locators_for_object(obj)

    # Create the gizmo for the object
    create_gizmo_curve(obj)

    print(f"\u2705 Locators and gizmo created for {obj}.")

    # Refresh the UI to add the new object
    open_object_selection_ui()

def open_object_selection_ui():
    """
    Opens a window listing all objects with locators.
    Adds a "Create" button to create locators and a gizmo on a new object.
    """
    if cmds.window("PivotObjectSelection", exists=True):
        cmds.deleteUI("PivotObjectSelection")

    cmds.window("PivotObjectSelection", title="Select an object", widthHeight=(300, 200))
    cmds.columnLayout(adjustableColumn=True)

    cmds.text(label="Select an object to manage its pivots:")

    cmds.separator(height=10)

    # Check which objects already have locators
    all_objects = cmds.ls(transforms=True)
    valid_objects = [obj for obj in all_objects if any(cmds.objExists(f"{loc}_{obj}") for loc in ["Origin", "PosPivot1", "PosPivot2"])]


    for obj in valid_objects:
        cmds.button(label=obj, command=lambda _, o=obj: open_pivot_ui(o))

    cmds.separator(height=10)
    cmds.button(label="Create", command=lambda _: create_locators_and_gizmo_for_selected_object())

    cmds.showWindow("PivotObjectSelection")

def open_pivot_ui(obj):
    """
    Opens the user interface to manage the pivots of the selected object.
    """
    if cmds.window("MovePivotAnimTool", exists=True):
        cmds.deleteUI("MovePivotAnimTool")

    cmds.window("MovePivotAnimTool", title=f"Pivots of {obj}", widthHeight=(300, 150))
    cmds.columnLayout(adjustableColumn=True)

    locators = create_locators_for_object(obj)

    for loc_name, locator in locators.items():
        cmds.button(label=f"Snap pivots to {loc_name}", command=lambda _, l=locator: snap_pivot_to_locator(obj, l))

    cmds.showWindow("MovePivotAnimTool")

# By Teo2103D

# Open the main window
open_object_selection_ui()

