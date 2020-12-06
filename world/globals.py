"""
Global variables and constants used in mud
"""
from enum import IntEnum

GOD_LVL = 205
WIZ_LVL = 204
IMM_LVL = 203
BUILDER_LVL = 202
HERO_LVL = 201

DEFAULT_MOB_STRUCT = {
    "key": "mob unfinished",
    "sdesc": "the unfinished mob",
    "ldesc": "An unfinished mob stands here",
    "edesc": "It looks unfinished",
    "position": "standing",
    "attack": "hit",
    "flags": [],
    "applies": [],
    "zone": "null",
    "stats": None  # default, holds an empty instance of MobStat class
}

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

DEFAULT_TRIG_STRUCT = {
    'name': 'unfinished trigger',
    'attachedto': '',
    'prog': ''
}

DAM_TYPES = {
    "physical": {
        "hit",
        "sting",
        "whip",
        "slash",
        "bite",
        "bludgeon",
        "crush",
        "pound",
        "claw",
        "maul",
        "blast",
        "punch",
        "thrash",
        "pierce",
        "scratch",
        "peck",
        "stab",
        "slap",
        "smash",
        "thwack",
        "claw",
        "cleave",
        "grep",
    },
    "magical": {
        "acidic", "chill", "freezing", "magic", "wrath", "flame",
        "divine_power", "smite", "shock"
    }
}

BOOK_CATEGORIES = ['fiction', 'religious', 'research', 'notes']

VALID_DIRECTIONS = ('north', 'south', 'east', 'west', 'up', 'down')

OPPOSITE_DIRECTION = {
    'north': 'south',
    'south': 'north',
    'east': 'west',
    'west': 'east',
    'up': 'down',
    'down': 'up'
}


class Positions(IntEnum):
    Dead = 0
    MortallyWounded = 1
    Incapacitated = 2
    Stunned = 3
    Sleeping = 4
    Resting = 5
    Sitting = 6
    Fighting = 7
    Standing = 8

    def members():
        return list(reversed(Positions._member_map_.keys()))


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


class _Proficiency:
    name = ""
    sdesc = ""
    pos = 0

    def __init__(self, **kwargs) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __repr__(self) -> str:
        return f"<{self.name}>"

    def all(self):
        return list(self.__dict__.keys())


class Untrained(_Proficiency):
    name = "untrained"
    sdesc = "No knowledge"
    pos = 0


class Novice(_Proficiency):
    name = 'novice'
    sdesc = "Rudimentary Knowledge"
    pos = 1


class Apprentice(_Proficiency):
    name = 'apprentice'
    sdesc = "Basic proficiency"
    pos = 2


class Journeyman(_Proficiency):
    name = 'journeyman'
    sdesc = "Hands on experience"
    pos = 3


class Adept(_Proficiency):
    name = "adept"
    sdesc = "Extensive experience or training"
    pos = 4


class Expert(_Proficiency):
    name = 'expert'
    sdesc = 'professinal level ability'
    pos = 5


class Master(_Proficiency):
    name = 'master'
    sdesc = "Complete mastery"
    pos = 6


_PROFICIENY_GRADIENT = {
    0: Untrained,
    1: Novice,
    2: Apprentice,
    3: Journeyman,
    4: Adept,
    5: Expert,
    6: Master
}