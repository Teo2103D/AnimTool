This script only works with human or humanoid rigs that have two legs and two arms.

The names of the locators are based on the highest group name in your hierarchy, so make sure to rename your group correctly before creating the locators.
Example: Jimmy_rig -> Arm_FK_Jimmy_rig_loc_R

Now, the IK/FK switch works with multiple rigs at the same time, and it also works if the rigs are imported as references.
A window opens asking which locator names you want to switch.
Example: In the scene, there are Arm_FK_PKPK_loc_R, Arm_FK_XUXU1_loc_R, Arm_FK_XUXU2_loc_R, Arm_FK_BABA1_loc_R, and Arm_FK_BABA2_loc_R. The window will allow you to choose between PKPK, XUXU, or BABA.

How it works:
Works with a rig that has 3 IK FK SK joint chains.

Step 1:
Find the IK joint chains. Select an IK joint chain in order (Shoulder -> Elbow -> Wrist for arms / Hip -> Knee -> Ankle for legs) and then place the basic locators (script: OnIk).
Repeat the action on Arm_L, Arm_R, Leg_L, and Leg_R.

Step 2:
Now select the "FK_wrist" joint so the IK control can snap to it.
Warning !!!
With AdvancedSkeleton, the IK controls do not have the same pivot point as the joints. In this case: select your IK control, run the OnIk script, then change the name of the Locator so that it is in IK mode, not FK (Ex : Leg_FK_gazelle1_loc_R to Leg_IK_gazelle1_loc_R). Then, delete the parent constraint of the locator and create a new parent constraint from the "FK_wrist" joint to your Locator.

Step 3:
Select an FK joint chain and run the OnFk script. Repeat the action on all IK joint chains: Arm_L, Arm_R, Leg_L, and Leg_R.

Now, you can do whatever you want with the created locators, group them and store them in the rig group or wherever, just don’t delete them.

SwitchIkFk:
The IK switch works only if 2 or 4 IK controls are selected. It is effective when the following controls are selected in this exact order: PV_ctrl -> IK_ctrl.

The FK switch works only if 3 or 6 FK controls are selected. It is effective when selected in the parent-to-child hierarchy order: Shoulder_ctrl -> Elbow_ctrl -> Wrist_ctrl / Hip_ctrl -> Knee_ctrl -> Ankle_ctrl.

Good animating :)