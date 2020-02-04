import curses

from .apps import App


@App.register("c")
class Keyboard:
    def __init__(self, observer, *a):
        self.keys = {"up": "^", "right": ">", "down": "v", "left": "<"}

        self.observer = observer
        self.buffer = None
        self._over = False

        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)

    def __del__(self):
        self._clean()

    def update(self, grid, _):
        self._buffer = grid
        self._draw()

    def getkey(self):
        key = self.stdscr.getkey()
        try:
            key = self.keys[key.lower().split("key_")[1]]
        except (KeyError, IndexError):
            pass
        return key


    def launch(self):
        try:
            while not self._over:
                self.observer(self.getkey())()
                self.stdscr.refresh()
                self._draw()
        finally:
            self._clean()

    def game_over(self):
        self._over = True

    def _clean(self):
        curses.nocbreak()
        self.stdscr.keypad(False)
        curses.echo()
        curses.endwin()

    def _draw(self):
        assert self._buffer is not None
        self.stdscr.addstr(0, 0, self._buffer)
