import maya.cmds as cmds

#By Teo2103D

def create_matched_groups_with_animation(obj_1, obj_2, start_frame, end_frame):
    """
    Crée deux groupes qui suivent les transformations des objets sélectionnés et anime le second objet
    pour qu'il suive le deuxième groupe entre les frames start_frame et end_frame.
    """
    if not cmds.objExists(obj_1) or not cmds.objExists(obj_2):
        cmds.warning("Un des objets sélectionnés n'existe plus !")
        return

    # Déplace la timeline à la frame de début avant de commencer les opérations
    cmds.currentTime(start_frame, edit=True)

    # Créer le premier groupe et le matcher au premier objet en world space
    grp_1 = cmds.group(empty=True, name="TeoOffset")
    cmds.xform(grp_1, ws=True, matrix=cmds.xform(obj_1, q=True, ws=True, matrix=True))

    # Ajouter une contrainte parent du premier groupe au premier objet
    cmds.parentConstraint(obj_1, grp_1, mo=True)

    # Créer le deuxième groupe et le matcher au deuxième objet en world space
    grp_2 = cmds.group(empty=True, name="TeoMAT")
    cmds.xform(grp_2, ws=True, matrix=cmds.xform(obj_2, q=True, ws=True, matrix=True))

    # Faire que grp_2 soit enfant de grp_1
    cmds.parent(grp_2, grp_1)

    # Appliquer un premier snap world space sur obj_2 à la frame start_frame
    cmds.currentTime(start_frame, edit=True)
    cmds.xform(obj_2, ws=True, matrix=cmds.xform(grp_2, q=True, ws=True, matrix=True))

    # Ajouter une clé d'animation sur le deuxième objet avant qu'il ne commence à suivre le groupe
    cmds.setKeyframe(obj_2, attribute=['translateX', 'translateY', 'translateZ', 
                                       'rotateX', 'rotateY', 'rotateZ', 
                                       'scaleX', 'scaleY', 'scaleZ'], time=start_frame-1)

    # Faire que le deuxième objet suive le deuxième groupe avec une clé d'animation à chaque frame
    for t in range(start_frame, end_frame + 1):
        cmds.currentTime(t, edit=True)
        cmds.xform(obj_2, ws=True, matrix=cmds.xform(grp_2, q=True, ws=True, matrix=True))
        cmds.setKeyframe(obj_2, attribute=['translateX', 'translateY', 'translateZ', 
                                           'rotateX', 'rotateY', 'rotateZ', 
                                           'scaleX', 'scaleY', 'scaleZ'], time=t)

    print(f"Groupes et animation créés :\n"
          f" - {grp_1} (matché sur {obj_1}, avec contrainte parent)\n"
          f" - {grp_2} (matché sur {obj_2}, et parenté à {grp_1})\n"
          f" - {obj_2} suit {grp_2} de la frame {start_frame} à {end_frame}, avec clés d'animation.")

    # Supprimer seulement le premier groupe
    cmds.delete(grp_1)

def open_ui():
    if cmds.window("ConstraintAnimTool", exists=True):
        cmds.deleteUI("ConstraintAnimTool")

    cmds.window("ConstraintAnimTool", title="FollowAnimTool", widthHeight=(300, 200))
    cmds.columnLayout(adjustableColumn=True)

    cmds.text(label="Frame de début :")
    start_frame_field = cmds.intField("startFrame", value=cmds.playbackOptions(query=True, minTime=True))

    cmds.text(label="Frame de fin :")
    end_frame_field = cmds.intField("endFrameField", value=cmds.playbackOptions(query=True, maxTime=True))

    cmds.button(label="Appliquer", command=lambda *_: create_matched_groups_with_animation(
        cmds.ls(selection=True)[0], cmds.ls(selection=True)[1], 
        cmds.intField(start_frame_field, query=True, value=True), 
        cmds.intField(end_frame_field, query=True, value=True)
    ))

    cmds.showWindow("ConstraintAnimTool")

# Ouvrir la fenêtre
open_ui()

#By Teo2103D
