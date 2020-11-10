from evennia.utils.utils import inherits_from, make_iter


class Attribute:
    def __init__(self, name, value=None):
        self.name = name
        self.value = value

        self.init()

    def __str__(self):
        return f"{self.name.capitalize()}: {self.value}"

    def __repr__(self):
        return f"{self.__class__.__name__}: <{self.name}:{self.value}>"

    def init(self):
        pass


class VitalAttribute(Attribute):
    def init(self):
        for k, v, in dict({
                'cur': 0,
                'max': -1,
                'mod': [],
                'rate': 1.0
        }).items():
            setattr(self, k, v)

    @property
    def mods(self):
        return sum(self.__dict__['mod'])

    def add_mod(self, value):
        self.__dict__['mod'].append(value)

    def remove_mod(self, value):
        self.__dict__['mod'].remove(value)

    def __str__(self):
        return f"{self.name.capitalize()}: {self.cur}/{self.max} [{self.mods}] x{self.rate}"

    def __repr__(self):
        return self.__str__()