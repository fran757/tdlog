from importlib import import_module

from .apps import App

for app in [".basic", ".curse", ".graphic"]:
    import_module(app, __package__)
