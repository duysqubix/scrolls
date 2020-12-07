"""
Base Mob class
Inherits the Character class, but isn't by default pupppeted.
"""

from world.conditions import Blinded, DarkSight, Flying, Hidden, Invisible, Sanctuary, Sneak, WaterWalking
from typeclasses.characters import DefaultCharacter


class Mob(DefaultCharacter):
    """
    base mob typeclass

    Extends the character typeclass, with a few exception.
    """
    def at_post_puppet(self):
        pass

    def at_pre_puppet(self):
        pass

    def at_post_unpuppet(self):
        pass

    def at_object_creation(self):
        self.db.is_npc = True
        self.db.is_pc = False


VALID_MOB_FLAGS = {
    'sentinel', 'scavenger', 'aware', 'aggr', 'stay_zone', 'memory', 'helper',
    'nosummon', 'noblind', 'nosleep'
}

VALID_MOB_APPLIES = {
    Blinded.__obj_name__, Invisible.__obj_name__, WaterWalking.__obj_name__,
    DarkSight.__obj_name__, Sanctuary.__obj_name__, Hidden.__obj_name__,
    Sneak.__obj_name__, Flying.__obj_name__
}
