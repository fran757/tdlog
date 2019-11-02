"""Grid to hold and manage grid items"""

import numpy as np
from .grid_item import ItemFactory
from . import item_types as types


class Grid:
    """Hold all grid content and handle movements."""

    def __init__(self, layout_path, check_wall=True):
        """Read file and store content, then update own cells."""
        self.items = []
        self.characters = {}

        try:
            layout_file = open(layout_path)
            cells = np.array([list(line)[:-1] for line in layout_file])
            for (i, j), cell in np.ndenumerate(cells):
                self.items.append(ItemFactory(cell)((i, j)))
            layout_file.close()
        except FileNotFoundError:
            raise FileNotFoundError(f"Invalid grid name : {layout_path}")

        # todo: self.shape ?
        self.height = max(i for i, _ in [item.coords for item in self.items]) + 1
        self.width = max(j for _, j in [item.coords for item in self.items]) + 1

        self.items = [item for item in self.items if not isinstance(item, types.Empty)]

        # handle specific types :
        def instances(cls, info):
            select = filter(lambda x: isinstance(x, cls), self.items)
            return {info(item): item for item in select}

        self.characters = instances(types.Character, str)
        arms = instances(types.Arm, lambda x: tuple(x.coords))
        pivots = instances(types.Pivot, lambda x: tuple(x.coords))

        for pivot in pivots.values():
            pivot.connect(arms)

        # self._connect_turnstiles(pivots, arms)
        self._update()
        if check_wall:
            self._check_grid()

    def _check_grid(self):
        """Forbid small or open map."""

        if max(self.width, self.height) < 5:
            raise Exception("Grid is too small")

        def walled(i, j, cell):
            is_border = i in [0, self.height - 1] or j in [0, self.width - 1]
            return not is_border or isinstance(cell, types.Wall)

        if not all(walled(i, j, cell) for (i, j), cell in np.ndenumerate(self.cells)):
            raise Exception("Build the wall")

    def _update(self):
        """Place items and fill up blanks."""
        self.cells = np.empty((self.height, self.width), types.Empty)
        for item in self.items:
            if item.is_active:
                self.cells[tuple(item.coords)] = item

        for (i, j), cell in np.ndenumerate(self.cells):
            if cell is None:
                self.cells[i, j] = types.Empty((i, j))

    def observe(self, coords):
        """Allow external to observe cell content."""
        return self.cells[tuple(coords)]

    def move(self, character_id, direction):
        """Handle movement of given character and direction.
        return whether any character won.
        """
        character = self.characters[character_id]
        direction = np.array(direction)
        if not character.is_active:
            return 0

        direction = np.array(direction)
        position = character.coords
        target_cell = self.cells[tuple(position + direction)]

        outcome = target_cell.request_move(position, direction, self.observe)
        if outcome == -1:
            character.is_active = False
            outcome = 0

        self._update()
        return outcome

    def __str__(self):
        return "\n".join(["".join([str(cell) for cell in row]) for row in self.cells])


if __name__ == "__main__":
    import doctest

    doctest.testmod()
