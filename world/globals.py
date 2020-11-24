"""
Global variables and constants used in mud
"""

GOD_LVL = 205
WIZ_LVL = 204
IMM_LVL = 203
BUILDER_LVL = 202
HERO_LVL = 201

DEFAULT_OBJ_STRUCT = {
    "key": "an unfinshed object",
    "sdesc": "an unfinshed object",
    "ldesc": "an unfinished object is lying here",
    "edesc": "",  # extra descrition when looked at
    "adesc": None,  # action desciption, message string announced when used
    "type":
    "default",  # type of object: book, weapon, equipment, scroll, etc...
    "weight": 0,
    "cost": 0,
    "level": 0,  # minimum level that can use this object
    "applies": [],  # affects object has on user (stat change, health, etc...)
    "tags": [],  # unique meta information about object itself
    "extra": {}  # holds special fields relatd to a special object
}

DEFAULT_ROOM_STRUCT = {
    "name": "an unfinished room",
    "zone": "null",
    "desc": "You are in an unfinished room.",
    'flags': [],
    'type': "inside",  # equiv of sector
    'exits': {
        'north': -1,
        'south': -1,
        'east': -1,
        'west': -1,
        'up': -1,
        'down': -1
    },
    'edesc': {},  # key/contents
    "extra": {}
}

DEFAULT_ZONE_STRUCT = {
    'name': "a new zone",
    'builders': [],
    'lifespan': -1,
    'level_range': [-1, -1],
    'reset_msg': "zone has reset"
}

DAM_TYPES = {
    "physical": {
        "hit", "sting", "whip", "slash", "bite", "bludgeon", "crush", "pound",
        "claw", "maul", "blast", "punch", "thrash", "pierce", "scratch",
        "peck", "stab", "slap", "smash", "thwack", "claw", "cleave", "grep", ""
    },
    "magical": {
        "acidic", "chill", "freezing", "magic", "wrath", "flame",
        "divine_power", "smite", "shock"
    }
}

VALID_DIRECTIONS = ('north', 'south', 'east', 'west', 'up', 'down')
OPPOSITE_DIRECTION = {
    'north': 'south',
    'south': 'north',
    'east': 'west',
    'west': 'east',
    'up': 'down',
    'down': 'up'
}


class _WearLocation:
    def __init__(self, name, display_msg=None):
        self.name = name
        self.display_msg = display_msg if display_msg else f"[|GWorn on {name.capitalize():<10}|n]"


WEAR_LOCATIONS = {
    _WearLocation("light", display_msg=f"[|GUsed as {'Light':<10}|n]"),
    _WearLocation("wield", display_msg=f"[|GWielded {'':<10}|n]"),
    _WearLocation("off-hand", display_msg=f"[|GOff-Hand {'':<9}|n]"),
    _WearLocation("head"),
    _WearLocation("back"),
    _WearLocation("shoulders"),
    _WearLocation("chest"),
    _WearLocation("arms"),
    _WearLocation("hands"),
    _WearLocation("l-finger"),
    _WearLocation("r-finger"),
    _WearLocation("legs"),
    _WearLocation("feet")
}


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
        return cls(0, "puny")

    @classmethod
    def tiny(cls):
        return cls(1, "tiny")

    @classmethod
    def small(cls):
        return cls(2, "small")

    @classmethod
    def standard(cls):
        return cls(3, "standard")

    @classmethod
    def large(cls):
        return cls(4, "large")

    @classmethod
    def huge(cls):
        return cls(5, "huge")

    @classmethod
    def enormous(cls):
        return cls(6, "enormous")