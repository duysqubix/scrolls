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
            # print(type(_v), type(name), type(value))
            _v[name] = value
            self.caller.attributes.add(self.__attr_name__, _v)

    def __str__(self):
        return f"{self.__attr_name__} on ({self.caller})"

    def __repr__(self):
        return str(self)

    def __getattr__(self, name):
        try:
            return self.caller.attributes.get(self.__attr_name__,
                                              default={})[name]
        except KeyError:
            return None

    def init(self):
        pass

    def all(self, return_obj=False):
        if not return_obj:
            return list(self.caller.attributes.get(self.__attr_name__).keys())
        objs = list(self.caller.attributes.get(self.__attr_name__).values())
        return [x for x in objs if x != self.__attr_name__]

    def get(self, name):
        return self.__getattr__(name)

    def set(self, name, value):
        self.__setattr__(name, value)
