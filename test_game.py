import os
import unittest
from model import Grid
from control import Game


def fixture_name(name):
    """return appropriate filename"""
    return os.getcwd() + "/fixtures/" + name + ".txt"


def build_fixture(name):
    """build game from fixture name"""
    return Game(Grid(fixture_name(name)), None)


def extract_fixture(name):
    """extract fixture data"""
    data = []
    with open(fixture_name(name)) as fixture:
        for line in fixture:
            data.append(line)
    return data


def repr_fixture(name):
    """return repr of fixture"""
    with open(fixture_name(name)) as fixture:
        return "".join(["".join(line) for line in fixture])


def write_fixture(data):
    """write fixture to tmp file"""
    with open(fixture_name("tmp"), "w") as tmp_file:
        print(data, file=tmp_file)


def expectation(move, expected):
    """Give fixture comparison result and related error message."""
    value = extract_fixture("tmp") == extract_fixture(expected)
    message = "Grid is not as expected after {} :\n".format(move) + repr_fixture("tmp")
    return value, message


class GlobalTest(unittest.TestCase):
    def test_all(self):
        """tests : 
        moving to empty cell
        moving into cell
        switching character
        turning turnstile
        blocked turnstile
        pushing crate into hole
        falling into hole
        """
        self.game = build_fixture("../model/grid")
        move = "1vv2^>3>>>"
        self.game.process_input(move)
        write_fixture(str(self.game.grid))
        self.assertTrue(*expectation(move, "global"))


if __name__ == "__main__":
    unittest.main()
