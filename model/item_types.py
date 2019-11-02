"""GridItem instances needed for the game."""

import numpy as np
from .grid_item import GridItem


Empty = GridItem("Empty", (), " ")
Wall = GridItem("Wall", (), "#", block=True)
Door = GridItem("Door", (), "@", win=True)
Character = GridItem("Character", (), list(map(str, range(1, 5))), block=True)


class Hole(metaclass=GridItem, die=True):
    """Absorb characters and get filled by crates."""

    skin = [".", "o", "O"]

    def fill(self):
        """Return whether crate falls in and fills self.
        In-game the hole doesn't survive being filled.
        A filled hole is still functionnal though (version 0).
        >>> hole = Hole((1,1),2)
        >>> hole.fill()
        True
        >>> hole.fill()
        True
        >>> hole.fill()
        False
        """

        fall = self.version > 0
        if fall:
            self.version -= 1
        if self.version <= 0:
            self.is_active = False
        return fall


class Crate(metaclass=GridItem):
    """Can be moved to fill holes."""

    skin = "*"

    def request_move(self, position, direction, observe):
        """Try to move the crate or push it in a hole."""
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


class Arm(metaclass=GridItem):
    """Is attached to Pivot by Turnstile.
    Turnstile handles movement.
    Unattached arms will not be considered by grid update.
    """

    skin = "/"

    def can_turn(self, rotation, position, observe):
        """Can the arm go through the next two cells
        given the rotation matrix and moving character position
        """
        # orientation and coords of obstacle
        orientation = np.copy(self.orientation)
        coords = np.copy(self.coords)
        for _ in range(2):
            orientation = np.dot(rotation, orientation)
            coords += orientation
            obstacle = observe(coords)
            if not ((coords == position).all() or isinstance(obstacle, (Empty, Arm))):
                return False
        return True

    def turn(self, rotation, pivot):
        """Rotate around pivot given the rotation matrix."""
        self.orientation = np.dot(rotation, self.orientation)
        self.coords = pivot + self.orientation


class Pivot(metaclass=GridItem, block=True):
    """Arms turn around self if pushed and free."""

    skin = "%"

    def connect(self, all_arms):
        """Register nearby arms as own.
        Give them the ability to turn around self.
        """
        self.arms = []
        for orientation in map(np.array, [[0, 1], [0, -1], [-1, 0], [1, 0]]):
            arm_coords = tuple(np.array(self.coords) + orientation)
            if arm_coords in all_arms:
                arm = all_arms[arm_coords]
                arm.orientation = orientation
                arm.request_move = self.move_arm
                self.arms.append(arm)

    def move_arm(self, position, direction, observe):
        """Turn around if enough room is available"""
        moment = np.sign(np.cross(position - self.coords, direction))
        rotation = moment * np.array([[0, -1], [1, 0]])
        if all(arm.can_turn(rotation, position, observe) for arm in self.arms):
            for arm in self.arms:
                arm.turn(rotation, self.coords)
            position += 2 * direction
        return 0
