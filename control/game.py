"""mediate interactions between model (Grid) and view (App) in standard MVC fashion"""


from .callback import observer


class Game:
    """create needed tools and start the game upon instanciation"""

    def __init__(self, grid, app_type):
        self.grid = grid
        self.commands = {"^": (-1, 0), ">": (0, 1), "v": (1, 0), "<": (0, -1)}

        keys = {"up": "^", "right": ">", "down": "v", "left": "<"}
        for key, symbol in keys.items():
            key = (f"key_{key}").upper()
            self.commands.update({key: self.commands[symbol]})
        self.active_character = "1"
        self.app = app_type

    @observer
    def callback(self, key):
        """pass key callback to model and update view"""
        self.process_input([key])
        self.app.update(str(self.grid), self.active_character)

        if key in map(str, range(1, 5)):
            key = str(int(key) % len(self.grid.characters) + 1)
        return key

    def process_input(self, commands):
        """Interpret a chain of user input and pass orders to grid."""
        for command in commands:
            dead = close = win = False
            if command == "q":
                close = True
            elif command in map(str, range(1, 5)):
                self.active_character = command
            elif self.active_character is None:
                raise Exception("No character is active")
            elif command in self.commands:
                win = self.grid.move(self.active_character, self.commands[command])
                dead = all(not char.is_active for char in self.grid.characters.values())

            if win or dead or close and self.app is not None:
                self.app.game_over()

    def play(self):
        """Launch the interactive game"""
        shape = (self.grid.height, self.grid.width)
        self.app = self.app(self.callback, shape, self.commands)
        self.app.update(str(self.grid), self.active_character)
        self.app.launch()
