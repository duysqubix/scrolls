class Characteristic:
    def __init__(self, name, short, base=0, bonus=0, favored=False):
        self.name = str(name)
        self.short = short
        self.base = base
        self.bonus = bonus
        self.favored = favored

    def __str__(self):
        return f"{self.__class__.__obj_name__}: <{self.base}/{self.bonus}>"

    def __repr__(self):
        return str(self)

    def __add__(self, other):
        if not isinstance(other, Characteristic):
            raise TypeError(f'can only add objs of {type(self)}')

        if self.name != other.name and self.short != other.short:
            raise ValueError('can only add characteristics of the same type')
        return self.__class__(base=(self.base + other.base),
                              bonus=(self.bonus + other.bonus),
                              favored=(self.favored or other.favored))

    def __sub__(self, other):
        char = self.__add__(-other)
        if char.base < 0:
            char.base = 0
        return char

    def __neg__(self):
        return self.__class__(base=-self.base,
                              bonus=-self.bonus,
                              favored=self.favored)

    def format(self):
        return "{:>12}: {:>3}({:>3})".format(self.name.capitalize(), self.base,
                                             self.bonus)


class StrChar(Characteristic):
    def __init__(self, base=0, bonus=0, favored=False):
        super(StrChar, self).__init__('strength', 'str', base, bonus, favored)


class EndChar(Characteristic):
    def __init__(self, base=0, bonus=0, favored=False):
        super(EndChar, self).__init__('endurance', 'end', base, bonus, favored)


class AgiChar(Characteristic):
    def __init__(self, base=0, bonus=0, favored=False):
        super(AgiChar, self).__init__('agility', 'agi', base, bonus, favored)


class IntChar(Characteristic):
    def __init__(self, base=0, bonus=0, favored=False):
        super(IntChar, self).__init__('intelligence', 'int', base, bonus,
                                      favored)


class WpChar(Characteristic):
    def __init__(self, base=0, bonus=0, favored=False):
        super(WpChar, self).__init__('willpower', 'wp', base, bonus, favored)


class PrcChar(Characteristic):
    def __init__(self, base=0, bonus=0, favored=False):
        super(PrcChar, self).__init__('persuasion', 'prc', base, bonus,
                                      favored)


class PrsChar(Characteristic):
    def __init__(self, base=0, bonus=0, favored=False):
        super(PrsChar, self).__init__('perception', 'prs', base, bonus,
                                      favored)


class LckChar(Characteristic):
    def __init__(self, base=0, bonus=0, favored=False):
        super(LckChar, self).__init__('luck', 'lck', base, bonus, favored)


CHARACTERISTICS = {
    'str': StrChar(),
    'end': EndChar(),
    'agi': AgiChar(),
    'int': IntChar(),
    'wp': WpChar(),
    'prc': PrcChar(),
    'prs': PrsChar(),
    'lck': LckChar()
}
