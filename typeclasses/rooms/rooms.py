"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom
from world.utils.utils import is_pc


class Room(DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """
    def announce(self, msg, exclude=[]):
        """send msg to all pcs in current room"""
        for obj in self.contents:
            if is_pc(obj) and obj not in exclude:
                obj.msg(msg)

    def at_object_creation(self):
        self.db.is_room = True