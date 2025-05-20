This script allows you to move the pivot point of any object whenever you want

To do this, simply:
- Open the script (a window opens).  
- Click on the object you want.  
- Press "Create." Two locators will now appear on your object (they can be moved as you like and are used to adjust the pivot).  
- If your window closes, reopen the script. The name of your object will now appear in the window.  
- Click on the button with your object's name (a new window appears).  
- This window displays the names of the two new locators for your object and the "Origin" button.  

Each click on a "Snap pivot..." button changes your object's pivot to the selected locator or back to the object's original pivot point. At the same time, it sets an animation key on your object's transforms as well as on the pivot point (the pivot keys are visible in the "Graph Editor"). This allows you to manage them as needed.  

The locators do not move the pivot point in real time; you must click "Snap pivot..." again to place the pivot at the desired locator.