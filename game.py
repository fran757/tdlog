"""
GridItem: content of one grid cell (always inherited before instanciation)
Turnstile: container for a more complex item
Grid: handles contents of the grid
Game: offers user IO and gameplay on the grid
"""

import numpy as np


COMMANDS = {"^": (-1, 0), ">": (0, 1), "v": (1, 0), "<": (0, -1)}


class GridItem:
    """default grid item, with coordinates and activity toggle"""

    skin = ""

    def __init__(self, coords):
        try:
            if len(coords) != 2:
                raise ValueError("coords should be 2D")
        except TypeError:
            raise TypeError("coords should be iterable")
        coords = np.array(coords)
        self.coords = coords
        self.is_active = True

    def __str__(self):
        """representation of the item when printing the grid"""
        if not isinstance(self.skin, str):
            raise TypeError("skin should be a string")
        return self.skin


# GridItems with externally handled functionality
Empty = type("Empty", (GridItem,), {"skin": " "})
Wall = type("Wall", (GridItem,), {"skin": "#"})
Door = type("Door", (GridItem,), {"skin": "@"})
Pivot = type("Pivot", (GridItem,), {"skin": "%"})


class Character(GridItem):
    """Unique playable entity"""

    skin = "1"

    def __init__(self, coords, name="0"):
        if not isinstance(name, str):
            raise TypeError("name should be a string")
        self.name = name
        self.skin = self.name
        super().__init__(coords)


class Hole(GridItem):
    """absorb characters unless filled by crate"""

    def __init__(self, coords, depth=1):
        if not (isinstance(depth, int) and depth > 0):
            raise ValueError("Depth should be a positive integer")
        if depth > 2:
            raise ValueError("Depth above 2 is not supported by the display")
        self.depth = depth
        super().__init__(coords)

    def fill(self):
        """recieve crate
        return whether crate fell
        >>> hole = Hole((1,1),2)
        >>> hole.fill()
        True
        >>> hole.fill()
        True
        >>> hole.fill()
        False
        """
        # if crate can fall in, depth decreases
        fall = self.depth > 0
        if fall:
            self.depth -= 1
        if self.depth <= 0:
            # hole is filled up if depth is zero
            self.is_active = False
        return fall

    def __str__(self):
        """skin depends on depth"""
        return [" ", "o", "O"][self.depth]


class Crate(GridItem):
    """can be moved to fill holes"""

    skin = "*"

    def request_move(self, position, direction, observe):
        """try to move the crate or push it in a hole"""
        target_coords = self.coords + direction
        target_cell = observe(target_coords)

        if isinstance(target_cell, Empty):
            # the crate can move to an empty cell only
            position += direction
            self.coords += direction
        elif isinstance(target_cell, Hole) and target_cell.fill():
            # if the hole is deep, the crate falls in
            position += direction
            self.coords += direction
            self.is_active = False
        return 0


class Arm(GridItem):
    """
    Is attached to Pivot by Turnstile
    Turnstile handles movement
    Unattached arms will not be considered by grid update
    """

    skin = "/"

    def __init__(self, coords, orientation):
        self.orientation = orientation
        self.turnstile = None
        super().__init__(coords)


class Turnstile:
    """Articulates arms around pivot"""

    def __init__(self, pivot, arms):
        self.pivot = pivot
        self.arms = arms
        for arm in self.arms:
            arm.request_move = self.request_move

    def request_move(self, position, direction, observe):
        """Turns around if enough room is available"""
        # moment of the action of character on arm : positive if counter-clockwise
        moment = np.sign(np.cross(position - self.pivot.coords, direction))
        rotation = moment * np.array([[0, -1], [1, 0]])
        for arm in self.arms:
            # check if arm can turn through next 2 cells, exit if it can't
            obstacle_orientation = np.copy(arm.orientation)
            obstacle_coords = np.copy(arm.coords)
            for _ in range(2):
                obstacle_orientation = np.dot(rotation, obstacle_orientation)
                obstacle_coords += obstacle_orientation
                obstacle = observe(obstacle_coords)
                if not (
                    (obstacle_coords == position).all()
                    or isinstance(obstacle, (Empty, Arm))
                ):
                    return 0
        for arm in self.arms:
            arm.orientation = np.dot(rotation, arm.orientation)
            arm.coords = self.pivot.coords + arm.orientation
        position += 2 * direction
        return 0


class Grid:
    """Hold all grid content and handle individual commands"""

    def __init__(self, layout_path, check_wall=True):
        """read file and store content, then update own cells"""
        pivots = []
        arms = []
        self.basic_items = []
        self.holes = []
        self.characters = {}
        self.turnstiles = []
        # grid dimensions calculated during file parsing
        self.width = 0
        self.height = 0
        with open(layout_path) as layout_file:
            for i, line in enumerate(layout_file):
                self.height += 1
                for j, cell in enumerate(line):
                    # identify cell type to handle specific cases

                    if cell == Empty.skin:
                        continue

                    # generic handling of basic items
                    for item_type in (Wall, Door, Crate):
                        if cell == item_type.skin:
                            self.basic_items.append(item_type((i, j)))

                    # generic handling of holes
                    for depth, skin in enumerate([" ", "o", "O"]):
                        if cell == skin:
                            self.basic_items.append(Hole((i, j), depth))

                    if cell in map(str, range(5)):
                        self.basic_items.append(Character((i, j), cell))
                        self.characters[cell] = self.basic_items[-1]
                    elif cell == "/":
                        arms.append((i, j))
                    elif cell == "%":
                        pivots.append((i, j))
                if self.width == 0:
                    self.width = len(line) - 1
                elif self.width != len(line) - 1:
                    raise Exception("Grid should be rectangular")
        self._connect_turnstiles(pivots, arms)
        self._update()
        if check_wall:
            self._check_grid()

    def _connect_turnstiles(self, pivots, arms):
        """connect arms to pivots given their coordinates"""
        for pivot in pivots:
            turnstile_arms = []
            orientations = map(np.array, [[0, 1], [0, -1], [-1, 0], [1, 0]])
            for orientation in orientations:
                # check if arms exist
                arm_coords = tuple(np.array(pivot) + orientation)
                if arm_coords in arms:
                    turnstile_arms.append(Arm(arm_coords, orientation))
            self.turnstiles.append(Turnstile(Pivot(pivot), turnstile_arms))

    def _check_grid(self):
        """check for small or open map"""
        # todo : fix nesting *********************************************************

        if max(self.width, self.height) < 5:
            raise Exception("Grid is too small")

        is_border = lambda i, j: i in [0, self.height - 1] or j in [0, self.width - 1]
        for i, row in enumerate(self.cells):
            for j, cell in enumerate(row):
                if is_border(i, j) and not isinstance(cell, Wall):
                    raise Exception(
                        "Build the wall {} {}".format(self.width, self.height)
                    )

    def _update(self):
        """
        Places every item at the right place on the grid
        """
        self.cells = np.empty((self.height, self.width), Empty)
        for item in self.basic_items:
            if item.is_active:
                self.cells[tuple(item.coords)] = item
        for turnstile in self.turnstiles:
            self.cells[tuple(turnstile.pivot.coords)] = turnstile.pivot
            for arm in turnstile.arms:
                self.cells[tuple(arm.coords)] = arm
        for i, row in enumerate(self.cells):
            for j, cell in enumerate(row):
                if cell is None:
                    self.cells[i, j] = Empty((i, j))

    def observe(self, coords):
        """allows external to observe cell content type"""
        return self.cells[tuple(coords)]

    def move(self, character_id, direction):
        """
        Handle movement of given character and direction
        Returns -1 if all characters are lost, 1 if a character wins, 0 otherwise
        """
        character = self.characters[character_id]
        if not character.is_active:
            print("Character is lost")
            return 0
        position = character.coords
        target_coords = position + direction
        target_cell = self.cells[tuple(target_coords)]
        outcome = 0
        if isinstance(target_cell, Empty):
            position += direction
            outcome = 0
        elif isinstance(target_cell, (Wall, Character, Pivot)):
            outcome = 0
        elif isinstance(target_cell, Door):
            position += direction
            outcome = 1
        elif isinstance(target_cell, Hole):
            position += direction
            if target_cell.depth > 0:
                character.is_active = False
            if all(not c.is_active for c in self.characters.values()):
                outcome = -1
            else:
                outcome = 0
        elif isinstance(target_cell, (Crate, Arm)):
            outcome = target_cell.request_move(position, direction, self.observe)
        self._update()
        return outcome

    def __str__(self):
        return "\n".join(["".join([str(cell) for cell in row]) for row in self.cells])


class Game:
    """Allows interaction with a grid"""

    def __init__(self, grid):
        self.commands = {"^": (-1, 0), ">": (0, 1), "v": (1, 0), "<": (0, -1)}
        self.grid = grid
        self.is_over = False
        self.active_character = "1"

    def process_input(self, commands):
        """Interpret a chain of user input and pass orders to grid"""
        for command in commands:
            if command == "q":
                self.is_over = True
                break
            if command in map(str, range(1, 5)):
                self.active_character = command
            elif self.active_character is None:
                raise Exception("No character is active")
            elif command in self.commands:
                direction = np.array(self.commands[command])
                outcome = self.grid.move(self.active_character, direction)
                if outcome != 0:
                    self.is_over = True

    def play(self):
        """game loop with user interaction"""
        print(self.grid)
        while not self.is_over:
            self.process_input(input())
            print(self.grid)
        print("Game Over")


if __name__ == "__main__":
    import doctest

    doctest.testmod()
    Game(Grid("grid.txt")).play()
