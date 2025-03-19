import maya.cmds as cmds

#By Teo2103D

# Stocker les objets ayant déjà des locators
tracked_objects = {}

import maya.cmds as cmds

def neutralize_pivot_effect(obj):
    """
    Trouve toutes les contraintes parent et point qui utilisent l'objet sélectionné comme cible,
    puis connecte un Multiply Divide Node et un PlusMinusAverage Node unique pour corriger les offsets sans créer de cycle.
    """
    if not cmds.objExists(obj):
        cmds.warning(f"L'objet {obj} n'existe pas !")
        return

    # Trouver toutes les contraintes parent et point dans la scène
    all_parent_constraints = cmds.ls(type="parentConstraint") or []
    all_point_constraints = cmds.ls(type="pointConstraint") or []
    
    relevant_constraints = []

    # Vérifier si l'objet est la cible des parentConstraints
    for constraint in all_parent_constraints:
        targets = cmds.parentConstraint(constraint, q=True, tl=True)
        if obj in targets:
            relevant_constraints.append(constraint)

    # Vérifier si l'objet est la cible des pointConstraints
    for constraint in all_point_constraints:
        targets = cmds.pointConstraint(constraint, q=True, tl=True)
        if obj in targets:
            relevant_constraints.append(constraint)

    if not relevant_constraints:
        cmds.warning(f"Aucune contrainte parent ou point affectant {obj} trouvée.")
        return

    # Créer un Multiply Divide Node pour inverser le Scale Pivot
    mult_node = f"{obj}_multReversePivot"
    if not cmds.objExists(mult_node):
        mult_node = cmds.createNode("multiplyDivide", name=mult_node)
        cmds.setAttr(f"{mult_node}.operation", 1)  # Multiplication
        cmds.setAttr(f"{mult_node}.input2X", -1)
        cmds.setAttr(f"{mult_node}.input2Y", -1)
        cmds.setAttr(f"{mult_node}.input2Z", -1)

    # Connecter le Scale Pivot de l'objet au Multiply Divide Node
    cmds.connectAttr(f"{obj}.scalePivotX", f"{mult_node}.input1X", force=True)
    cmds.connectAttr(f"{obj}.scalePivotY", f"{mult_node}.input1Y", force=True)
    cmds.connectAttr(f"{obj}.scalePivotZ", f"{mult_node}.input1Z", force=True)

    # Appliquer la connexion aux contraintes trouvées
    for constraint in relevant_constraints:
        # Déterminer si c'est une parentConstraint ou une pointConstraint
        is_parent_constraint = cmds.objectType(constraint) == "parentConstraint"

        # Obtenir les offsets avant connexion
        if is_parent_constraint:
            offset_x = cmds.getAttr(f"{constraint}.target[0].targetOffsetTranslateX")
            offset_y = cmds.getAttr(f"{constraint}.target[0].targetOffsetTranslateY")
            offset_z = cmds.getAttr(f"{constraint}.target[0].targetOffsetTranslateZ")
        else:
            offset_x = cmds.getAttr(f"{constraint}.offsetX")
            offset_y = cmds.getAttr(f"{constraint}.offsetY")
            offset_z = cmds.getAttr(f"{constraint}.offsetZ")

        # Créer un seul PlusMinusAverage Node par contrainte
        add_node = cmds.createNode("plusMinusAverage", name=f"{constraint}_addOffset")
        cmds.setAttr(f"{add_node}.operation", 1)  # Mode addition

        # Mettre les valeurs actuelles des offsets dans les Add nodes
        cmds.setAttr(f"{add_node}.input1D[1]", offset_x)  # X → input1D
        cmds.setAttr(f"{add_node}.input2D[1].input2Dx", offset_y)  # Y → input2Dx
        cmds.setAttr(f"{add_node}.input3D[1].input3Dx", offset_z)  # Z → input3Dx

        # Connecter le Multiply Divide Node au Add Node pour chaque axe
        cmds.connectAttr(f"{mult_node}.outputX", f"{add_node}.input1D[0]", force=True)  # X
        cmds.connectAttr(f"{mult_node}.outputY", f"{add_node}.input2D[0].input2Dx", force=True)  # Y
        cmds.connectAttr(f"{mult_node}.outputZ", f"{add_node}.input3D[0].input3Dx", force=True)  # Z

        # Connecter les Add Nodes aux offsets des contraintes respectives
        if is_parent_constraint:
            cmds.connectAttr(f"{add_node}.output1D", f"{constraint}.target[0].targetOffsetTranslateX", force=True)
            cmds.connectAttr(f"{add_node}.output2D.output2Dx", f"{constraint}.target[0].targetOffsetTranslateY", force=True)
            cmds.connectAttr(f"{add_node}.output3D.output3Dx", f"{constraint}.target[0].targetOffsetTranslateZ", force=True)
        else:
            cmds.connectAttr(f"{add_node}.output1D", f"{constraint}.offsetX", force=True)
            cmds.connectAttr(f"{add_node}.output2D.output2Dx", f"{constraint}.offsetY", force=True)
            cmds.connectAttr(f"{add_node}.output3D.output3Dx", f"{constraint}.offsetZ", force=True)

    print(f" Pivot de {obj} neutralisé sur ses contraintes parent et point avec un seul PlusMinusAverage par contrainte.")


def create_locators_for_object(obj):
    """
    Crée trois locators (Origine, PosPivot1, PosPivot2) dans le bon ordre :
    - Création du locator
    - Parenter le locator à l'objet sélectionné
    - Snap au world space de l'objet
    - Mettre les valeurs de translation et rotation du locator à 0
    """
    if obj in tracked_objects:
        return tracked_objects[obj]  # Retourner les locators existants

    locators = {}
    locator_names = ["Origine", "PosPivot1", "PosPivot2"]

    # Obtenir la position world space de l'objet
    obj_world_pos = cmds.xform(obj, q=True, ws=True, rp=True)

    for loc_name in locator_names:
        full_name = f"{loc_name}_{obj}"

        if cmds.objExists(full_name):
            locators[loc_name] = full_name
        else:
            loc = cmds.spaceLocator(name=full_name)[0]

            # Parenter d'abord le locator à l'objet sélectionné
            cmds.parent(loc, obj)

            # Snapper le locator à la position world space de l'objet
            cmds.xform(loc, ws=True, t=obj_world_pos)

            # Remettre translation et rotation à 0 sans freeze
            cmds.setAttr(f"{loc}.translate", 0, 0, 0)
            cmds.setAttr(f"{loc}.rotate", 0, 0, 0)

            # Mettre les valeurs de scale à 1
            cmds.setAttr(f"{loc}.scale", 1, 1, 1)

            locators[loc_name] = loc

            # Rendre "Origine" invisible
            if loc_name == "Origine":
                cmds.setAttr(f"{loc}.visibility", 0)

            # Changer la couleur de PosPivot1 et PosPivot2
            if loc_name == "PosPivot1":
                cmds.setAttr(f"{loc}.overrideEnabled", 1)
                cmds.setAttr(f"{loc}.overrideColor", 17)  # Jaune

            if loc_name == "PosPivot2":
                cmds.setAttr(f"{loc}.overrideEnabled", 1)
                cmds.setAttr(f"{loc}.overrideColor", 16)  # Blanc

    tracked_objects[obj] = locators  # Stocker les locators pour cet objet
    return locators

def create_gizmo_curve(obj):
    """
    Crée un gizmo en forme de croix avec une sphère qui suit le pivot de l'objet.
    - Le gizmo est d'abord parenté à l'objet.
    - Il est ensuite aligné au pivot en world space.
    - Enfin, il est reset en translation, rotation et scale avant d'être contraint.
    """

    # Supprimer l'ancien gizmo s'il existe
    gizmo_name = f"gizmoCurve_{obj}"
    if cmds.objExists(gizmo_name):
        cmds.delete(gizmo_name)

    # Créer les segments des axes en courbe
    axis_curves = []
    axis_points = [
        [(0, 0, 0), (2, 0, 0)],  # X
        [(0, 0, 0), (0, 2, 0)],  # Y
        [(0, 0, 0), (0, 0, 2)],  # Z
    ]
    
    for points in axis_points:
        curve = cmds.curve(d=1, p=points, k=[0, 1])
        axis_curves.append(curve)

    # Créer les sphères en courbe
    sphere1 = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), r=1.5, sections=20)[0]
    sphere2 = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), r=1.5, sections=20)[0]
    sphere3 = cmds.circle(nr=(0, 0, 1), c=(0, 0, 0), r=1.5, sections=20)[0]

    # Créer le groupe gizmo
    gizmo_curve_group = cmds.group(empty=True, name=gizmo_name)

    # Parenter les courbes directement sous le groupe
    for curve in axis_curves + [sphere1, sphere2, sphere3]:
        cmds.parent(curve, gizmo_curve_group)

    # Activer l'affichage "reference" pour éviter la sélection accidentelle
    for curve in axis_curves + [sphere1, sphere2, sphere3]:
        cmds.setAttr(f"{curve}.overrideEnabled", 1)
        cmds.setAttr(f"{curve}.overrideDisplayType", 2)

    # **1. Parentage à l'objet AVANT toute transformation**
    cmds.parent(gizmo_curve_group, obj)

    # **2. Snap au world pivot**
    pivot_position = cmds.xform(obj, query=True, worldSpace=True, rp=True)
    cmds.xform(gizmo_curve_group, worldSpace=True, translation=pivot_position)

    # **3. Reset des valeurs (garde le bon alignement)**
    cmds.setAttr(f"{gizmo_curve_group}.translate", 0, 0, 0)
    cmds.setAttr(f"{gizmo_curve_group}.rotate", 0, 0, 0)
    cmds.setAttr(f"{gizmo_curve_group}.scale", 0.25, 0.25, 0.25)

    # **4. Contraintes pour suivre l'objet**
    cmds.orientConstraint(obj, gizmo_curve_group, maintainOffset=True)
    cmds.pointConstraint(obj, gizmo_curve_group, maintainOffset=True)

    print(f"\u2705 Gizmo Curve pour {obj} créé proprement avec reset et contraintes.")

def snap_pivot_to_locator(obj, locator):
    """
    Permet de snapper le pivot de l'objet à la position du locator donné (rotationPivot et scalePivot),
    et d'ajouter des clés d'animation sur tous les attributs du pivot de l'objet à la frame actuelle.
    """
    # Obtenir la position du locator dans l'espace monde
    locator_pos = cmds.xform(locator, q=True, ws=True, t=True)

    # Obtenir la frame actuelle pour y ajouter une clé d'animation
    current_frame = cmds.currentTime(query=True)

    # Déplacer les pivots de l'objet sans déplacer l'objet lui-même
    cmds.xform(obj, ws=True, rp=locator_pos)  # Rotation pivot
    cmds.xform(obj, ws=True, sp=locator_pos)  # Scale pivot

    # Ajouter des clés d'animation sur tous les attributs des pivots et des transforms
    # Clé pour le rotationPivot (rp) et scalePivot (sp)
    cmds.setKeyframe(obj, attribute="rotatePivot", t=current_frame)
    cmds.setKeyframe(obj, attribute="scalePivot", t=current_frame)
    
    # Clé pour la translation et la rotation des pivots (même si les valeurs sont 0)
    cmds.setKeyframe(obj, attribute="rotatePivotTranslate", t=current_frame)
    cmds.setKeyframe(obj, attribute="scalePivotTranslate", t=current_frame)

    # Clé pour la translation et la rotation de l'objet lui-même (au cas où)
    cmds.setKeyframe(obj, attribute="translate", t=current_frame)
    cmds.setKeyframe(obj, attribute="rotate", t=current_frame)

    print(f" Les pivots de rotation et de mise à l'échelle de {obj} ont été snapés à {locator}, et des clés d'animation ont été ajoutées.")

def create_locators_and_gizmo_for_selected_object():
    """
    Crée les locators et le gizmo pour l'objet sélectionné et rafraîchit l'UI.
    """
    selected = cmds.ls(selection=True)
    if not selected:
        cmds.warning("Veuillez sélectionner un objet avant de créer des locators et un gizmo.")
        return

    obj = selected[0]

    # Créer les offsets pour l'objet
    neutralize_pivot_effect(obj)

    # Créer les locators pour l'objet
    create_locators_for_object(obj)

    # Créer le gizmo pour l'objet
    create_gizmo_curve(obj)

    print(f"\u2705 Locators et gizmo créés pour {obj}.")

    # Rafraîchir l'UI pour ajouter le nouvel objet
    open_object_selection_ui()

def open_object_selection_ui():
    """
    Ouvre une fenêtre listant tous les objets ayant des locators.
    Ajoute un bouton "Create" pour créer des locators et un gizmo sur un nouvel objet.
    """
    if cmds.window("PivotObjectSelection", exists=True):
        cmds.deleteUI("PivotObjectSelection")

    cmds.window("PivotObjectSelection", title="Sélectionner un objet", widthHeight=(300, 200))
    cmds.columnLayout(adjustableColumn=True)

    cmds.text(label="Sélectionnez un objet pour gérer ses pivots :")

    cmds.separator(height=10)

    # Vérifier quels objets ont déjà des locators
    all_objects = cmds.ls(transforms=True)
    valid_objects = [obj for obj in all_objects if any(cmds.objExists(f"{loc}_{obj}") for loc in ["Origine", "PosPivot1", "PosPivot2"])]


    for obj in valid_objects:
        cmds.button(label=obj, command=lambda _, o=obj: open_pivot_ui(o))

    cmds.separator(height=10)
    cmds.button(label="Create", command=lambda _: create_locators_and_gizmo_for_selected_object())

    cmds.showWindow("PivotObjectSelection")

def open_pivot_ui(obj):
    """
    Ouvre l'interface utilisateur pour gérer les pivots de l'objet sélectionné.
    """
    if cmds.window("PivotAnimTool", exists=True):
        cmds.deleteUI("PivotAnimTool")

    cmds.window("PivotAnimTool", title=f"Pivots de {obj}", widthHeight=(300, 150))
    cmds.columnLayout(adjustableColumn=True)

    locators = create_locators_for_object(obj)

    for loc_name, locator in locators.items():
        cmds.button(label=f"Snap pivots à {loc_name}", command=lambda _, l=locator: snap_pivot_to_locator(obj, l))

    cmds.showWindow("PivotAnimTool")

#By Teo2103D

# Ouvrir la fenêtre principale
open_object_selection_ui()
