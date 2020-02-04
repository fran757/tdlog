"""Interactive applications for command line or GUI gameplay."""

from .apps import App


@App.register("t")
class Basic:
    """Command line gameplay."""

    def __init__(self, observer, *a):
        self.observer = observer
        self._buffer = None
        self._over = False

    def update(self, grid, _):
        """Register grid changes."""
        if self._buffer is None:
            print(grid)
        self._buffer = grid

    def _draw(self):
        """Print last version of grid registered."""
        print(self._buffer)

    def launch(self):
        """Enter game mainloop."""
        while not self._over:
            for key in input():
                self.observer(key)()
            self._draw()

    def game_over(self):
        """Verify mainloop exit condition"""
        self._over = True
