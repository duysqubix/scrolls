"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia import DefaultRoom
from evennia.utils import inherits_from


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
            if inherits_from(obj, 'typeclasses.characters.Character'):
                if obj in exclude:
                    continue
                obj.msg(msg)