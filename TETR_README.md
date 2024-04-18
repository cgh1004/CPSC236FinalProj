# Modded Tetris
## How To Run: 
Ensure you have all three of the tetrisModded.py, tetrisb.mid, and tetrisc.mid files in the same directory. \
Ensure you have Python 3+ and Pygames downloaded and in your PATH. \
Run tetrisModded.py in the editor of your choice or on the comand line. \
Command: `python .\tetrisModded.py` \
The game will pop up in a separate window.

## How to Play:
Clear as many lines as you can, and don't let the pieces reach the top! \
By default, you can move pieces sideways with the arrow keys, down slowly with the down key, down immediately with space, rotate counterclockwise with z, and clockwise with x. \
You can "hold" a piece for later and release it with c. \
To pause, hit p, to exit, hit ESC. \
For settings, press 1! You can change any of these keys in settings. \
Stack pieces and try to fill the board horizontally, when you fill a line horizontally it will disappear and give you points! 

## Inspiration: 
I have taken inspiration from TETR.IO by osk.  I reccommend playing this as well, it is a much better and very fun version of this program!

## Settings Screen
### About
I added the capability to switch to a settings screen at any point in the game by hitting the `1` key \
This settings screen display all the hotkeys used for controlling the game. They can be changed by \
Clicking any setting (e.g. Left: left), where it will then go into edit mode (it will show a flashing cursor). \
Once hitting a different hotkey, the hotkey mapped to that action will be changed to whichever key the user chooses. \
For example, if the user decides they want to move a falling tetrimino left with the A key, they can click the `left` setting, \
then hit `A`. This change will be immediately displayed, and can be seen in use once switching out of the settings screen. \
The settings screen can be switched to and from using the settings hotkey, which can also be changed.


## Hold Capability
### About
I have added the ability to save a piece for later, and the default key for this action is `C`. \
This enables the user to strategically plan their next move and pull off a more sophisticated game. \
"Held" pieces are placed to the left of the board for convenient visualization. \
Holding involves placing the current falling key aside and pushing in a new piece in its place-- the first time the user holds, it will push in the next piece. All times after that, it will swap in the piece in the hold space. \
You can only hold once per drop! Hold is disabled for a held piece, place it down to re-load you hold abilities!

## Pseudorandom Bag
### About
Originally, the game fully randomized which shape would fall. \
I have changed this so that the fall of pieces is still random, but within a "bag". \
The pieces are now randomized within the 7 pieces Once all pieces have been randomly picked from the "bag", the bag resets and all pieces are available again. \
This guarantees the reception of at least one of each piece per seven pieces fallen, letting the user concoct plans and gameplay.

## Other Changes:
### Rotation
I have de-randomized the rotation of the falling pieces. \
Originally, pieces spawned into the board at a random rotation. \
This could cause unexpected game terminations when an I piece spawns in vertically, so I have standardized which rotation each piece will spawn in with. \