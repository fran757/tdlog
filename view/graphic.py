import sys
import os
import numpy as np

import PyQt5.QtWidgets as widgets
import PyQt5.QtGui as gui


class Graphic(widgets.QWidget):
    """GUI gameplay with PyQt"""

    def __init__(self, observer, shape, commands):
        self.main = widgets.QApplication(sys.argv)
        super().__init__(None)
        self.shape = shape

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

        self.icons = {}
        for symbol, name in icon_map.items():
            self.icons[symbol] = gui.QPixmap(
                os.getcwd() + "/view/images/{}.png".format(name)
            )
        self.grid = np.empty(self.shape, widgets.QLabel)

        self._init_ui(observer, commands)

    def _cells(self):
        """offer easy iteration over grid coordinates"""
        for i in range(self.shape[0]):
            for j in range(self.shape[1]):
                yield i, j

    def _init_ui(self, observer, commands):
        """Setup GUI layout and widgets"""
        self.setWindowTitle("Kwirk")
        self.setGeometry(100, 100, 0, 0)
        self.layout = widgets.QGridLayout()
        self.layout.setSpacing(0)

        for i, j in self._cells():
            self.grid[i, j] = widgets.QLabel()
            self.layout.addWidget(self.grid[i, j], i, j)

        self.controls = []
        for symbol, direction in commands.items():
            button = widgets.QPushButton(self)
            button.setText(symbol)
            position = [(1 + direction[0]), self.shape[1] + (1 + direction[1])]
            self.layout.addWidget(button, *position, 1, 1)
            button.clicked.connect(observer(symbol))

        self.character_button = widgets.QPushButton(self)
        self.character_button.setIcon(gui.QIcon(self.icons["1"]))
        self.character_button.clicked.connect(observer("2"))
        self.layout.addWidget(self.character_button, 1, self.shape[1] + 1, 1, 1)

        self.setLayout(self.layout)
        self.show()

    def update(self, grid, active_character):
        """Update grid display and character switch iconi."""
        data = np.array([list(line) for line in grid.split("\n")])
        assert data.shape == self.shape
        for i, j in self._cells():
            self.grid[i, j].setPixmap(self.icons[data[i, j]])
        self.character_button.setIcon(gui.QIcon(self.icons[active_character]))

    def launch(self):
        """Enter game mainloop."""
        sys.exit(self.main.exec_())

    def game_over(self):
        """Exit mainloop."""
        self.close()
