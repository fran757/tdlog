import unittest
import game


def fixture_name(name):
    """return appropriate filename"""
    return "fixtures/" + name + ".txt"


def build_fixture(name):
    """build game from fixture name"""
    return game.Game(game.Grid(fixture_name(name), False))


def extract_fixture(name):
    """extract fixture data"""
    data = []
    with open(fixture_name(name)) as fixture:
        for line in fixture:
            data.append(line)
    return data


def fixtures_are_same(*names):
    """check if named fixtures are identical"""
    datas = list(map(extract_fixture, names))
    return all([data == datas[0] for data in datas])


def repr_fixture(name):
    """return repr of fixture"""
    with open(fixture_name(name)) as fixture:
        return "".join(["".join(line) for line in fixture])


def write_fixture(data):
    """write fixture to tmp file"""
    with open(fixture_name("tmp"), "w") as tmp_file:
        print(data, file=tmp_file)


def message_fixture(move):
    return "Grid is not as expected after {} :\n".format(move) + repr_fixture("tmp")


class TurnstileTest(unittest.TestCase):
    def test_basic(self):
        """full rotation of the turnstile"""
        self.game = build_fixture("turnstile/basic_0")
        for n, move in enumerate([">", "v", "<", "^"]):
            self.game.process_input(move)
            write_fixture(str(self.game.grid))
            expected_grid_name = "turnstile/basic_{}".format((n + 1) % 4)
            self.assertTrue(
                fixtures_are_same("tmp", expected_grid_name), message_fixture(move)
            )

    def test_block(self):
        """blocked turnstile"""
        for block_id in (0, 1):
            block_name = "turnstile/block_{}".format(block_id)
            self.game = build_fixture(block_name)
            self.game.process_input(">")
            write_fixture(str(self.game.grid))
            self.assertTrue(fixtures_are_same("tmp", block_name), message_fixture(">"))


if __name__ == "__main__":
    unittest.main()
