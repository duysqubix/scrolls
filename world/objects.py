"""
Defines the prototype for objects in game.

Things like book, scrolls, weapons, armor, etc...
"""
DEFAULT_OBJ_STRUCT = {
    'key': "an unfinshed object",
    'sdesc': "an unfinshed object",
    'ldesc': "an unfinished object is lying here",
    "adesc": None,  # action desciption, message string announced when used
    "type": None,  # type of object: book, weapon, equipment, scroll, etc...
    "wear_flags": None,  #take, head, armor, wield, shield, etc..
    "weight": 0,
    "cost": 0,
    "level": 0,  # minimum level that can use this object
    "applies":
    []  # temporarily changes stats, attrs, and conditions while using
}


class Object:
    def __init__(self, **kwargs):
