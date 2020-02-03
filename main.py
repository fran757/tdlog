#!/usr/bin/env python3.7
"""flags : -t for command line gameplay, GUI by default"""

import os
import sys
from control import Game
from model import Grid
from view import Graphic, Basic, Keyboard

if __name__ == "__main__":
    AppType = Graphic  # default value for now

    # class registration design could be used also but not today
    app_types = {"-t": Basic, "-g": Graphic, "-k": Keyboard}
    if len(sys.argv) > 1:
        flag = sys.argv[1]
        if flag not in app_types:
            raise KeyError(f"Incorrect flag: {flag}")
        AppType = app_types[flag]

    Game(Grid(os.getcwd() + "/model/grid.txt"), AppType).play()
