class StorageHandler:
    __attr_name__ = ""

    def __init__(self, caller):
        self.caller = caller
        # self.integrity_check()
        self.init()

    def __getattr__(self, _attr):
        return None

    def __setattr__(self, name, value):
        super().__setattr__(name, value)

        if name not in ['caller']:
            self.caller.attributes.get(self.__attr_name__)[name] = value

    def __str__(self):
        return f"{self.__attr_name__} on ({self.caller})"

    def __repr__(self):
        return str(self)

    def __getattr__(self, name):
        return self.caller.attributes.get(self.__attr_name__)[name]

    def init(self):
        pass

    def all(self):
        return list(self.caller.attributes.get(self.__attr_name__).keys())

    def get(self, name):
        return eval(f"self.{name}")
