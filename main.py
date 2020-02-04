#!/usr/bin/env python3.7
"""flags : -t for command line gameplay, GUI by default"""

import os
import sys
from control import Game
from model import Grid
from view import App


def main():
    try:
        key = sys.argv[1].split("-", 1)[1]
    except:
        key = "c"

    path = os.getcwd() + "/model/grid.txt"

    Game(Grid(path), App(key)).play()


if __name__ == "__main__":
    main()
