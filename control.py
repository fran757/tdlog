"""mediate interactions between model (Grid) and view (App) in standard MVC fashion"""

import game
import view


class Callback:
    """(callable) call method on parent with client-defined key"""

    def __init__(self, key, parent, method):
        print(type(method))
        self.key = key
        self.parent = parent
        self.on_call = method

    def __call__(self):
        self.key = self.on_call(self.parent, self.key)


def observer(method):
    """allow creation of custom (key) callback to controller"""

    def callback_factory(parent, key):
        return Callback(key, parent, method)

    return callback_factory


class Controller:
    """create needed tools and start the game upon instanciation"""

    def __init__(self, file_name):
        self.grid = game.Grid(file_name)
        self.game = game.Game(self.grid)
        self.icon_map = {
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
            self.icon_map[str(i)] = "char{}".format(i)

        self.app = view.App(
            self.grid.height,
            self.grid.width,
            self.icon_map,
            game.COMMANDS,
            self.callback,
        )

        self.app.draw(str(self.grid))
        self.app.launch()

    @observer
    def callback(self, key):
        """pass key callback to model and update view"""
        assert isinstance(self, Controller)
        if key in map(str, range(1, 5)):
            key = str(int(key) % len(self.grid.characters) + 1)
            self.app.current_character = key
        self.game.process_input([key])
        self.app.draw(str(self.grid))
        return key


if __name__ == "__main__":
    Controller("grid.txt")
