class StorageHandler:
    __attr_name__ = ""

    def __init__(self, caller):
        self.caller = caller
        self.name = self.__attr_name__
        self.init()

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name not in ['caller']:
            _v = self.caller.attributes.get(self.__attr_name__, default={})
            _v[name] = value
            self.caller.attributes.add(self.__attr_name__, _v)

    def __str__(self):
        return f"{self.__attr_name__} on ({self.caller})"

    def __repr__(self):
        return str(self)

    def __getattr__(self, name):
        return self.caller.attributes.get(self.__attr_name__)[name]

    def init(self):
        pass

    @property
    def all(self):
        return list(self.caller.attributes.get(self.__attr_name__).keys())

    def get(self, name):
        return self.__getattr__(name)

    def set(self, name, value):
        self.__setattr__(name, value)
