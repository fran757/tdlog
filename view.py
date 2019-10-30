import sys
import numpy as np
import PyQt5.QtWidgets as widgets  # import QApplication, QWidget
import PyQt5.QtGui as gui


class App(widgets.QWidget):
    def __init__(self, grid_height, grid_width, icon_map, commands, observer):
        self.main = widgets.QApplication(sys.argv)
        super().__init__(None)
        self.grid_width = grid_width
        self.grid_height = grid_height

        self.title = "Kwirk"
        self._current_character = "1"

        self.icons = {}
        for symbol, name in icon_map.items():
            self.icons[symbol] = gui.QPixmap("images/{}.png".format(name))
        self.grid = np.empty((self.grid_height, self.grid_width), widgets.QLabel)

        self.commands = commands
        self.initUI(observer)

    @property
    def current_character(self):
        return self._current_character

    @current_character.setter
    def current_character(self, value):
        self._current_character = value
        self.character_button.setIcon(gui.QIcon(self.icons[value]))

    def initUI(self, observer):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 0, 0)
        self.layout = widgets.QGridLayout()

        for i in range(self.grid_height):
            for j in range(self.grid_width):
                self.grid[i, j] = widgets.QLabel()
                self.layout.addWidget(self.grid[i, j], i, j)

        self.controls = []
        for symbol, direction in self.commands.items():
            button = widgets.QPushButton(self)
            button.setText(symbol)
            position = [(1 + direction[0]), self.grid_width + (1 + direction[1])]
            self.layout.addWidget(button, *position, 1, 1)
            button.clicked.connect(observer(symbol))

        self.character_button = widgets.QPushButton(self)
        self.character_button.setIcon(gui.QIcon(self.icons[self._current_character]))
        self.character_button.clicked.connect(observer(self.current_character))
        self.layout.addWidget(self.character_button, 1, self.grid_width + 1, 1, 1)

        self.setLayout(self.layout)
        self.show()

    def draw(self, grid):
        data = np.array([list(line) for line in grid.split("\n")])
        assert data.shape == (self.grid_height, self.grid_width)
        for i in range(self.grid_height):
            for j in range(self.grid_width):
                self.grid[i, j].setPixmap(self.icons[data[i, j]])

    def launch(self):
        sys.exit(self.main.exec_())


if __name__ == "__main__":
    import game

    icon_map = {
        " ": "empty",
        "*": "crate",
        "O": "deep_hole",
        "o": "hole",
        "@": "door",
        "%": "turnstile_axis",
        "/": "turnstile_block",
        "#": "wall",
    }
    for i in range(1, 5):
        icon_map[str(i)] = "char{}".format(i)

    observer = lambda a,b:0

    g = game.Game(game.Grid("grid.txt"))
    ex = App(g.grid.height, g.grid.width, icon_map, game.COMMANDS, observer)
    ex.draw(str(g.grid))
