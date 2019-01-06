# README #

# Autoclicker.
- Uses a key and mouse combo to activate clicking, then listens for either another key combo, or mouse movement to stop clicking. Closes on esc keypress.
- Defaults k = activate, l = deactivate, delay = .0334 seconds. ~30 clicks per second. 5 second delay after clicking activation before movement will kill the clicks. k + click again to re-activate.
- Instructions:
    - Install pynput per the requirements.txt file. Preferably into a virtualenv.
    - Launch the program with python 3.4+.
    - Press and hold the letter k then left click to start the autoclicker. You have 5 seconds to place the mouse in it's final position before any movement will kill the clicking.
    - Press l to deactivate clicking.
    - Press Esc to quit.
