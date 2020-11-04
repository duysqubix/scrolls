class StorageHandler:
    __attr_name__ = ""

    def __init__(self, caller):
        self.caller = caller
        self.integrity_check()
        self.init()

    def __getattr__(self, _attr):
        return None

    def __str__(self):
        return f"{self.__attr_name__} on ({self.caller})"

    def __repr__(self):
        return str(self)

    def init(self):
        pass

    def get(self, id):
        return self.__dict__[id]

    def get_raw(self, name):
        return self.caller.attributes.get(self.__attr_name__)['name']

    def all(self):
        return [x for x in self.__dict__.keys() if x not in ['caller']]

    def integrity_check(self):
        for k, v in self.caller.attributes.get(self.__attr_name__,
                                               dict()).items():
            setattr(self, k, v)
