import maya.cmds as cmds
import sys
import os
import importlib

#By Teo2103D

# Automatically retrieves the "scripts" folder path in Maya
maya_scripts_path = os.path.join(os.path.expanduser("~"), "Documents", "maya", "scripts")
sys.path.append(maya_scripts_path)

def run_follow_tool(*args):
    """Loads and executes FollowAnimTool.py"""
    try:
        import FollowAnimTool
        importlib.reload(FollowAnimTool)
    except Exception as e:
        cmds.warning(f"FollowAnimTool Error: {e}")

def run_UnlockRot_ScalePivot(*args):
    """Loads and executes UnlockRot_ScalePivot.py"""
    try:
        import UnlockRot_ScalePivot
        importlib.reload(UnlockRot_ScalePivot)
    except Exception as e:
        cmds.warning(f"UnlockRot_ScalePivot Error: {e}")
        
def run_move_pivot_tool(*args):
    """Loads and executes MovePivotTool.py"""
    try:
        import MovePivotTool
        importlib.reload(MovePivotTool)
    except Exception as e:
        cmds.warning(f"MovePivotTool Error: {e}")

def run_SetUpSwitch_OnIk_tool(*args):
    """Loads and executes OnIk.py"""
    try:
        import OnIk
        importlib.reload(OnIk)
    except Exception as e:
        cmds.warning(f"OnIk Error: {e}")

def run_SetUpSwitch_OnFk_tool(*args):
    """Loads and executes OnFk.py"""
    try:
        import OnFk
        importlib.reload(OnFk)
    except Exception as e:
        cmds.warning(f"OnFk Error: {e}")

def run_Switch_FkIk_tool(*args):
    """Loads and executes SwitchIkFk.py"""
    try:
        import SwitchIkFk
        importlib.reload(SwitchIkFk)
    except Exception as e:
        cmds.warning(f"SwitchIkFk Error: {e}")

# Reset functions
def reset_to_defaults(option, *args):
    selected_objects = cmds.ls(selection=True)
    if not selected_objects:
        cmds.warning("Please select at least one object.")
        return
    
    for obj in selected_objects:
        if option == "All":
            attributes = cmds.listAttr(obj, keyable=True) or []
            for attr in attributes:
                default_value = cmds.attributeQuery(attr, node=obj, listDefault=True)
                if default_value:
                    try:
                        cmds.setAttr(f"{obj}.{attr}", default_value[0])
                    except:
                        pass
        elif option == "Transforms":
            for transform in ["translate", "rotate", "scale"]:
                for axis in "XYZ":
                    attr = f"{transform}{axis}"
                    if cmds.attributeQuery(attr, node=obj, exists=True):
                        try:
                            default_value = cmds.attributeQuery(attr, node=obj, listDefault=True)
                            if default_value:
                                cmds.setAttr(f"{obj}.{attr}", default_value[0])
                        except:
                            pass
        elif option == "Other":
            transform_attrs = {f"{t}{a}" for t in ["translate", "rotate", "scale"] for a in "XYZ"}
            attributes = cmds.listAttr(obj, keyable=True) or []
            for attr in attributes:
                if attr not in transform_attrs:
                    default_value = cmds.attributeQuery(attr, node=obj, listDefault=True)
                    if default_value:
                        try:
                            cmds.setAttr(f"{obj}.{attr}", default_value[0])
                        except:
                            pass
    print(f"Reset {option} completed.")

def reset_selected_attributes(*args):
    selected_objects = cmds.ls(selection=True)
    if not selected_objects:
        cmds.warning("No object selected.")
        return
    selected_attrs = cmds.channelBox("mainChannelBox", query=True, selectedMainAttributes=True)
    if not selected_attrs:
        cmds.warning("No attributes selected in the Channel Box.")
        return
    for obj in selected_objects:
        for attr in selected_attrs:
            default_value = cmds.attributeQuery(attr, node=obj, listDefault=True)
            if default_value:
                try:
                    cmds.setAttr(f"{obj}.{attr}", default_value[0])
                except:
                    pass
    print("Reset of selected attributes completed.")


def create_anim_tool_menu():
    """Creates a custom 'AnimTool' menu in Maya"""
    menu_name = "AnimToolMenu"

    # Deletes the old menu if it already exists
    if cmds.menu(menu_name, exists=True):
        cmds.deleteUI(menu_name)

    # Creates the menu in Maya's main window
    cmds.menu(menu_name, label="AnimTool", parent="MayaWindow", tearOff=True)
    
    # Adds options to the menu
    cmds.menuItem(label="Follow Tool", command=run_follow_tool)
   
    # Créez le sous-menu "Pivot" sous le menu principal
    pivot_menu = cmds.menuItem(label="Pivot Tool", subMenu=True, parent=menu_name, tearOff=True)  # Spécifiez explicitement `parent=menu_name`
    cmds.menuItem(label="Move Pivot Tool", parent=pivot_menu, command=run_move_pivot_tool)
    cmds.menuItem(label="Unlock Pivot", parent=pivot_menu, command=run_UnlockRot_ScalePivot)

    # Créez le sous-menu "SwitchIkFk" sous le menu principal
    switch_menu = cmds.menuItem(label="Switch IkFk", subMenu=True, parent=menu_name, tearOff=True)  # Spécifiez explicitement `parent=menu_name`
    cmds.menuItem(label="Loc On Ik", parent=switch_menu, command=run_SetUpSwitch_OnIk_tool)
    cmds.menuItem(label="Loc On Fk", parent=switch_menu, command=run_SetUpSwitch_OnFk_tool)
    cmds.menuItem(label="Switch", parent=switch_menu, command=run_Switch_FkIk_tool)
    
    # Créez le sous-menu "Reset" sous le menu principal
    reset_menu = cmds.menuItem(label="Reset", subMenu=True, parent=menu_name, tearOff=True)  # Spécifiez explicitement `parent=menu_name`
    cmds.menuItem(label="All", parent=reset_menu, command=lambda _: reset_to_defaults("All"))
    cmds.menuItem(label="Transforms Only", parent=reset_menu, command=lambda _: reset_to_defaults("Transforms"))
    cmds.menuItem(label="Other (Attributes Only)", parent=reset_menu, command=lambda _: reset_to_defaults("Other"))
    cmds.menuItem(label="Selection Attributes", parent=reset_menu, command=reset_selected_attributes)

# Executes the script to create the menu
create_anim_tool_menu()
