"""
Room

Rooms are simple containers that has no location of their own.

"""

from world.utils.db import search_roomdb
from world.globals import DEFAULT_ROOM_STRUCT
from evennia import DefaultRoom, GLOBAL_SCRIPTS, search_object
from world.utils.utils import delete_contents, is_pc, EntityLoader


class Room(DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """
    __room_type__ = ""
    __specific_fields__ = {}
    __help_msg__ = ""

    def announce(self, msg, exclude=[]):
        """send msg to all pcs in current room"""
        for obj in self.contents:
            if is_pc(obj) and obj not in exclude:
                obj.msg(msg)

    def reset(self, populate=True):
        """resets room and populates based on load_list"""
        self.at_object_creation()

        if populate:
            # clear room first
            delete_contents(self)
            yaml_str = self.db.load_list
            if not yaml_str:
                return

            for obj in EntityLoader.read(self, yaml_str):
                obj.load()

            self.announce("reset complete")

    def at_object_creation(self):

        # this is built-in Limbo id, #1 is superuser
        if not self.attributes.has('is_room'):
            self.db.is_room = True

        if self.key == "Limbo":
            key = 1
            self.key = 1
            room = {
                "name": "The Void of Magnus",
                "zone": "void",
                "desc": "You float aimlessly in Magnus's void",
                "flags": ["safe", "no_trans", "indoors"],
                "type": "void",
                "exits": {
                    "north": -1,
                    "south": -1,
                    "east": -1,
                    "west": -1,
                    "up": -1,
                    "down": -1
                },
                "edesc": {},
                "extra": {}
            }
            GLOBAL_SCRIPTS.roomdb.vnum[1] = room
        key = int(self.key)
        # room = dict(GLOBAL_SCRIPTS.roomdb.vnum[int(key)])
        room = search_roomdb(vnum=key)
        if not room:
            raise NotImplementedError(
                "attempting to create a room that doesn't exist in blueprint database"
            )
        room = room[key]
        # set fields that didn't exist before, mostly used
        # if future fields are added and old already created objs
        # don't know about them.
        for field, default_value in DEFAULT_ROOM_STRUCT.items():
            try:
                _ = room[field]
            except KeyError:
                room[field] = default_value

        self.db.name = room['name']
        self.db.zone = room['zone']
        self.db.desc = room['desc']
        self.db.flags = room['flags']
        self.db.sector = room['type']
        self.db.exits = room['exits']
        self.db.edesc = room['edesc']
        self.db.extra = room['extra']
        self.db.load_list = room['load_list']

        for efield, evalue in self.__specific_fields__.items():
            if efield in self.db.extra.keys():
                self.attributes.add(efield, self.db.extra[efield])
            else:
                self.attributes.add(efield, evalue)


class RoomSector:
    def __init__(self, name, symbol):
        self.name = name
        self.symbol = symbol  # for maps


VALID_ROOM_FLAGS = {
    'dark', 'fear', 'indoors', 'law', 'newbies', 'nowhere', 'no_mob',
    'no_gate', 'no_recall', 'no_summon', 'no_teleport', 'no_trans', 'private',
    'safe', 'silence', 'solitary'
}

VALID_ROOM_SECTORS = {
    'inside': RoomSector('inside', '.'),
    'city': RoomSector('city', '|xC|n'),
    'field': RoomSector('field', '|g,|n'),
    'forest': RoomSector('forest', '|GY|n'),
    'hills': RoomSector('hills', '|mm|n'),
    'mountain': RoomSector('mountain', '|RM|n'),
    'water': RoomSector('water', '|C~|n'),
    'sky': RoomSector('sky', '|c^|n'),
    'underwater': RoomSector('underwater', '|BU|n'),
    'void': RoomSector('void', '|x-|n')
}


def get_room(vnum):
    room = search_object(str(vnum), typeclass=Room)
    if not room:
        return None
    return room[0]
