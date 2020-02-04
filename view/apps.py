class App:
    registered={}

    def __new__(cls, key):
        return cls.registered[key]

    @classmethod
    def register(cls, key):
        def deco(app):
            try:
                cls.registered[key] = app
            except KeyError as ke:
                raise ke(f"Unregistered app: {key}")
            return app
        return deco
