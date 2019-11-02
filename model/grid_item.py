"""simplify grid item type and grid item instanciation"""

import numpy as np


class _ItemBase:
    """base class for GridItem instanciation
    version needed in case of multiple skins"""

    skin = ""

    def __init__(self, coords, version=0):
        try:
            if len(coords) != 2:
                raise ValueError("coords should be 2D")
        except TypeError:
            raise TypeError("coords should be iterable")
        coords = np.array(coords)
        if not isinstance(version, int):
            raise TypeError(f"version should be int, not {type(version)}")

        self.coords = coords
        self.version = version
        self.is_active = True

    def __str__(self):
        """representation of the item when printing the grid"""
        skins = self.skin if isinstance(self.skin, list) else [self.skin]
        if not isinstance(skins[self.version], str):
            raise TypeError(f"skin should be a string, not {self.skin}")
        return skins[self.version]


class ItemFactory:
    """GridItem class instanciation by skin"""

    _registery = {}

    @classmethod
    def register(cls, item_type, skin, *key):
        """register item_type by skin
        will pass version key at instanciation implicitly
        """

        assert len(key) <= 1
        if not isinstance(skin, str):
            raise TypeError("skin should be a string")

        if skin in cls._registery:
            raise ValueError(f"{skin} is already registered")
        cls._registery[skin] = lambda *args: item_type(*(args + key))

    def __init__(self, skin):
        self.skin = skin

    def __call__(self, *args, **kwargs):
        return self._registery[self.skin](*args, **kwargs)


class GridItem(type):
    """GridItem instance will inherit from _ItemBase
    general inheritance is supported but unused for now
    GridItems will be registered into ItemFactory by their skin(s)"""

    def __new__(cls, name, bases, attrs, win=False, block=False, die=False):
        # making sure skin is defined
        if not isinstance(attrs, dict):
            attrs = {"skin": attrs}
        elif "skin" not in attrs:
            raise ValueError(f"{name} has no skin")

        # making sure item will handle player movement
        @staticmethod
        def request_move(position, direction, _):
            if not block:
                position += direction
            return 1 if win else -1 if die else 0

        if "request_move" not in attrs:
            attrs["request_move"] = request_move

        # making sure _ItemBase is a base class
        if not list(filter(lambda base: isinstance(base, _ItemBase), bases)):
            bases += (_ItemBase,)

        # item class instanciation
        new_item = super().__new__(cls, name, bases, attrs)

        # item class registration
        skin = attrs["skin"]
        if isinstance(skin, list):
            for key, version in enumerate(skin):
                ItemFactory.register(new_item, version, key)
        else:
            ItemFactory.register(new_item, skin)

        return new_item
