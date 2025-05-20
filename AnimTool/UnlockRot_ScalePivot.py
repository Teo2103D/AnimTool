import maya.cmds as cmds

#By Teo2103D

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
                
# Appeler la fonction pour déverrouiller les pivots des objets sélectionnés
unlock_pivot_attributes()
