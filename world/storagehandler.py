class StorageHandler:
    __attr_name__ = ""

    def __init__(self, caller):
        self.caller = caller
        self.update()

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        attr = self.caller.attributes.get(self.__attr_name__, dict())
        attr[name] = value

    def __getattr__(self, _attr):
        return None

    def __str__(self):
        return f"{self.__attr_name__} on ({self.caller})"

    def __repr__(self):
        return str(self)

    def all(self):
        return [x for x in self.__dict__.keys() if x not in ['caller']]

    def update(self):
        for k, v in self.caller.attributes.get(self.__attr_name__,
                                               dict()).items():
            setattr(self, k, v)

        
