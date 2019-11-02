"""'Parent can pass own method to client for generic feedback."""


class Callback:
    """Call method on parent with client-defined key."""

    def __init__(self, key, parent, method):
        # could be a dataclass but not worth the update
        self.key = key
        self.parent = parent
        self.method = method

    def __call__(self):
        self.key = self.method(self.parent, self.key)


def observer(method):
    """Return factory that takes one (key) argument from client."""

    def callback_factory(parent, key):
        return Callback(key, parent, method)

    return callback_factory
