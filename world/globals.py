"""
Global variables and constants used in mud
"""

GOD_LVL = 205
WIZ_LVL = 204
IMM_LVL = 203
BUILDER_LVL = 202
HERO_LVL = 201


class Size:
    """
    Defines sizes of objects. Overrides multiple magic methods
    in order to 
    """
    def __init__(self, size, name):
        self.name = name
        self.size = size

    def __gt__(self, other):
        return self.size > other.size

    def __lt__(self, other):
        return self.size < other.size

    def __eq__(self, other):
        return self.size == other.size

    def __ne__(self, other):
        return self.size != other.size

    def __ge__(self, other):
        return self.size >= other.size

    def __le__(self, other):
        return self.size <= other.size

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"{self.name}({self.size})"

    @classmethod
    def puny(cls):
        return cls(0, 'puny')

    @classmethod
    def tiny(cls):
        return cls(1, 'tiny')

    @classmethod
    def small(cls):
        return cls(2, 'small')

    @classmethod
    def standard(cls):
        return cls(3, 'standard')

    @classmethod
    def large(cls):
        return cls(4, 'large')

    @classmethod
    def huge(cls):
        return cls(5, 'huge')

    @classmethod
    def enormous(cls):
        return cls(6, 'enormous')