import maya.cmds as cmds
import re

# By Teo2103D

def detect_unique_locator_names():
    locators = cmds.ls(type="locator")

    if not locators:
        cmds.error("Aucun locator trouvé dans la scène.")

    unique_names = set()
    # Regex améliorée pour éviter "PV_" et retirer les chiffres et underscores finaux
    name_pattern = re.compile(r"(?:Arm|Leg)_(?:FK|IK|IK_PV)_([A-Za-z_]+?)\d*_loc_[LR]")

    for locator in locators:
        match = name_pattern.search(locator)
        if match:
            name = match.group(1)
            # Supprime "PV_" s'il est présent au début
            clean_name = re.sub(r"^PV_", "", name)
            # Supprime tous les underscores à la fin du nom (évite "jeff_rig_" au lieu de "jeff_rig")
            clean_name = clean_name.rstrip("_")
            unique_names.add(clean_name)

    if not unique_names:
        cmds.error("Aucun nom valide trouvé dans les locators.")
        return

    window_name = "locatorNamesWindow"
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)

    cmds.window(window_name, title="Noms uniques des locators", widthHeight=(300, 200))
    cmds.columnLayout(adjustableColumn=True)
    cmds.text(label="Noms trouvés dans les locators :")
    locator_list = cmds.textScrollList(allowMultiSelection=False, height=150)

    for name in unique_names:
        cmds.textScrollList(locator_list, edit=True, append=name)

    cmds.button(label="Sélectionner le groupe", command=lambda x: apply_group_selection(locator_list))
    cmds.showWindow(window_name)

def apply_group_selection(locator_list):
    selected_group = cmds.textScrollList(locator_list, q=True, selectItem=True)

    if not selected_group:
        cmds.error("Veuillez sélectionner un groupe de locators.")
        return

    selected_group = selected_group[0]
    match_transforms_to_locators(selected_group)

# Fonction pour trouver un objet même avec un namespace
def find_object_with_partial_name(target_name):
    all_objects = cmds.ls(long=True)

    for obj in all_objects:
        if target_name in obj:
            return obj  # Retourne le premier objet correspondant

    return None  # Aucun objet trouvé

# Fonction pour déterminer la catégorie (bras ou jambe) des objets sélectionnés
def determine_category(selected_objects):
    arm_list = ["wrist", "hand", "elbow", "arm", "shoulder", "clavicle", "poignet", "main", "coude", "bras", "epaule", "clavicule"]
    leg_list = ["hip", "pelvis", "femur", "kneecap", "knee", "leg", "ankle", "foot", "tibia", "hanche", "bassin", "rotule", "genou", "cheville", "pied", "waist", "hinge", "heel", "toe"]

    is_arm = any(any(word.lower() in obj.lower() for word in arm_list) for obj in selected_objects)
    is_leg = any(any(word.lower() in obj.lower() for word in leg_list) for obj in selected_objects)

    if is_arm and is_leg:
        cmds.error("La sélection contient des objets des deux groupes 'bras' et 'jambe'.")
        return None
    elif is_arm:
        return "arm"
    elif is_leg:
        return "leg"
    else:
        cmds.error("La sélection ne correspond à aucun groupe valide ('arm' ou 'leg').")
        return None

# Fonction pour appliquer les alignements pour FK locators
def match_to_fk_locators(selected_objects, category, selected_group):
    def get_suffix(obj_name):
        if obj_name.endswith('_L'):
            return '_L'
        elif obj_name.endswith('_R'):
            return '_R'
        else:
            return ''

    objects_L = [obj for obj in selected_objects if get_suffix(obj) == '_L']
    objects_R = [obj for obj in selected_objects if get_suffix(obj) == '_R']
    objects_none = [obj for obj in selected_objects if get_suffix(obj) == '']

    def get_locators(objects, suffix):
        locators = []
        for i, obj in enumerate(objects):
            if category == "arm":
                locator_name = f"Arm_FK_{selected_group}_{i+1}_loc{suffix}"
            elif category == "leg":
                locator_name = f"Leg_FK_{selected_group}_{i+1}_loc{suffix}"
            else:
                locator_name = f"{selected_group}_FK_{selected_group}_{i+1}_loc{suffix}"

            # Trouver l'objet en prenant en compte le namespace
            full_locator_name = find_object_with_partial_name(locator_name)

            if full_locator_name:
                locators.append(full_locator_name)
            else:
                cmds.warning(f"Le locator {locator_name} n'existe pas.")
        return locators

    locators_L = get_locators(objects_L, '_L')
    locators_R = get_locators(objects_R, '_R')
    locators_none = get_locators(objects_none, '')

    for obj in selected_objects:
        suffix = get_suffix(obj)
        locator_to_match = None
        if suffix == '_L' and locators_L:
            locator_to_match = locators_L.pop(0)
        elif suffix == '_R' and locators_R:
            locator_to_match = locators_R.pop(0)
        elif suffix == '' and locators_none:
            locator_to_match = locators_none.pop(0)

        if locator_to_match:
            cmds.matchTransform(obj, locator_to_match, position=True, rotation=True, scale=False)
            print(f"Alignement effectué : {obj} -> {locator_to_match}")

# Fonction pour appliquer les alignements pour IK locators
def match_to_ik_locators(selected_objects, category, selected_group):
    def get_suffix(obj_name):
        if obj_name.endswith('_L'):
            return '_L'
        elif obj_name.endswith('_R'):
            return '_R'
        else:
            return ''

    suffix_counts = {"_L": 0, "_R": 0, "": 0}

    for obj in selected_objects:
        suffix = get_suffix(obj)
        suffix_counts[suffix] += 1
        if suffix_counts[suffix] > 2:
            cmds.error(f"Vous ne pouvez pas sélectionner plus de deux objets avec le suffixe '{suffix}'.")

    last_suffix = None

    for obj in selected_objects:
        current_suffix = get_suffix(obj)

        if last_suffix is None or last_suffix != current_suffix:
            if category == "arm":
                locator_name = f"Arm_IK_PV_{selected_group}_loc{current_suffix}"
            elif category == "leg":
                locator_name = f"Leg_IK_PV_{selected_group}_loc{current_suffix}"
            else:
                locator_name = f"{selected_group}_IK_PV_{selected_group}_loc{current_suffix}"
        else:
            if category == "arm":
                locator_name = f"Arm_IK_{selected_group}_1_loc{current_suffix}"
            elif category == "leg":
                locator_name = f"Leg_IK_{selected_group}_1_loc{current_suffix}"
            else:
                locator_name = f"{selected_group}_IK_{selected_group}_1_loc{current_suffix}"

        full_locator_name = find_object_with_partial_name(locator_name)

        if full_locator_name:
            cmds.matchTransform(obj, full_locator_name, position=True, rotation=True, scale=False)
            print(f"Alignement effectué : {obj} -> {full_locator_name}")
        else:
            cmds.warning(f"Le locator {locator_name} n'existe pas pour l'objet {obj}.")

        last_suffix = current_suffix

# Fonction principale pour appliquer les alignements aux locators
def match_transforms_to_locators(selected_group):
    selected_objects = cmds.ls(selection=True)
    
    if len(selected_objects) == 0:
        cmds.error("Veuillez sélectionner au moins un objet.")
        return

    category = determine_category(selected_objects)

    if len(selected_objects) in [3, 6]:
        match_to_fk_locators(selected_objects, category, selected_group)
    elif len(selected_objects) in [2, 4]:
        match_to_ik_locators(selected_objects, category, selected_group)
    else:
        cmds.error(f"Le script fonctionne uniquement avec 2, 4, 3 ou 6 objets sélectionnés. Vous avez sélectionné {len(selected_objects)}.")

# Exécuter la détection des locators
detect_unique_locator_names()

# By Teo2103D
