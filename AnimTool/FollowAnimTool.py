import maya.cmds as cmds

# By Teo2103D

def create_matched_groups_with_animation(obj_1, obj_2, start_frame, end_frame):
    """
    Creates two groups that follow the transformations of the selected objects and animates the second object
    so that it follows the second group between the start_frame and end_frame.
    """
    if not cmds.objExists(obj_1) or not cmds.objExists(obj_2):
        cmds.warning("One of the selected objects no longer exists!")
        return

    # Move the timeline to the start frame before starting operations
    cmds.currentTime(start_frame, edit=True)

    # Create the first group and match it to the first object in world space
    grp_1 = cmds.group(empty=True, name="TeoOffset")
    cmds.xform(grp_1, ws=True, matrix=cmds.xform(obj_1, q=True, ws=True, matrix=True))

    # Add a parent constraint from the first object to the first group
    cmds.parentConstraint(obj_1, grp_1, mo=True)

    # Create the second group and match it to the second object in world space
    grp_2 = cmds.group(empty=True, name="TeoMAT")
    cmds.xform(grp_2, ws=True, matrix=cmds.xform(obj_2, q=True, ws=True, matrix=True))

    # Make grp_2 a child of grp_1
    cmds.parent(grp_2, grp_1)

    # Apply an initial world space snap on obj_2 at the start_frame
    cmds.currentTime(start_frame, edit=True)
    cmds.xform(obj_2, ws=True, matrix=cmds.xform(grp_2, q=True, ws=True, matrix=True))

    # Add an animation keyframe for the second object before it starts following the group
    cmds.setKeyframe(obj_2, attribute=['translateX', 'translateY', 'translateZ', 
                                       'rotateX', 'rotateY', 'rotateZ', 
                                       'scaleX', 'scaleY', 'scaleZ'], time=start_frame-1)

    # Make the second object follow the second group with an animation keyframe for each frame
    for t in range(start_frame, end_frame + 1):
        cmds.currentTime(t, edit=True)
        cmds.xform(obj_2, ws=True, matrix=cmds.xform(grp_2, q=True, ws=True, matrix=True))
        cmds.setKeyframe(obj_2, attribute=['translateX', 'translateY', 'translateZ', 
                                           'rotateX', 'rotateY', 'rotateZ', 
                                           'scaleX', 'scaleY', 'scaleZ'], time=t)

    print(f"Groups and animation created:\n"
          f" - {grp_1} (matched to {obj_1}, with parent constraint)\n"
          f" - {grp_2} (matched to {obj_2}, and parented to {grp_1})\n"
          f" - {obj_2} follows {grp_2} from frame {start_frame} to {end_frame}, with animation keys.")

    # Delete only the first group
    cmds.delete(grp_1)

def open_ui():
    if cmds.window("ConstraintAnimTool", exists=True):
        cmds.deleteUI("ConstraintAnimTool")

    cmds.window("ConstraintAnimTool", title="FollowAnimTool", widthHeight=(320, 100))
    cmds.columnLayout(adjustableColumn=True)

    cmds.text(label="Start Frame:")
    start_frame_field = cmds.intField("startFrame", value=cmds.playbackOptions(query=True, minTime=True))

    cmds.text(label="End Frame:")
    end_frame_field = cmds.intField("endFrameField", value=cmds.playbackOptions(query=True, maxTime=True))

    cmds.button(label="Apply", command=lambda *_: create_matched_groups_with_animation(
        cmds.ls(selection=True)[0], cmds.ls(selection=True)[1], 
        cmds.intField(start_frame_field, query=True, value=True), 
        cmds.intField(end_frame_field, query=True, value=True)
    ))

    cmds.showWindow("ConstraintAnimTool")

# Open the window
open_ui()

# By Teo2103D
