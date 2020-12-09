"""
Base Mob class
Inherits the Character class, but isn't by default pupppeted.
"""
import copy
from world.traits import DiseaseResistTrait, DiseasedTrait, ImmunityTrait
from world.globals import Positions
from evennia import GLOBAL_SCRIPTS

from evennia.utils.dbserialize import deserialize

from world.characteristics import CHARACTERISTICS
from world.conditions import Blinded, DarkSight, DetectHidden, DetectInvis, Diseased, Flying, Hidden, Invisible, Sanctuary, Silenced, Sneak, WaterWalking, get_condition
from typeclasses.characters import Character


class Mob(Character):
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

    def at_cmdset_get(self, **kwargs):
        # do not give npc other cmdsets made for character
        pass

    def at_object_creation(self):
        self.db.look_index = 1
        self.db.attrs = {}
        self.db.stats = {}
        self.db.skills = {}
        self.db.languages = {}
        self.db.conditions = {'conditions': []}
        self.db.traits = {'traits': []}
        self.db.stats = copy.deepcopy(CHARACTERISTICS)
        self.db.is_npc = True
        self.db.is_pc = False

        obj = deserialize(GLOBAL_SCRIPTS.mobdb.vnum[int(self.key)])

        self.db.key = obj['key']
        self.db.sdesc = obj['sdesc']
        self.db.ldesc = obj['ldesc']
        self.db.edesc = obj['edesc']
        self.db.attack = obj['attack']
        self.db.flags = obj['flags']

        # special attributes

        # positions is an IntEnum so we can use sleeping<standing == True
        self.db.position = Positions.members(return_dict=True)[obj['position']]

        # applies, here actually apply them
        for condition in obj['applies']:
            self.conditions.add(get_condition(con_name=condition))

        self.db.zone = obj['zone']

        self.add_attr('level', obj['level'])

        # do stats here


VALID_MOB_FLAGS = {
    'sentinel', 'scavenger', 'aware', 'aggr', 'stay_zone', 'memory', 'helper',
    'nosummon', 'noblind', 'nosleep', 'nokill'
}

VALID_MOB_APPLIES = {
    Blinded.__obj_name__, Invisible.__obj_name__, WaterWalking.__obj_name__,
    DarkSight.__obj_name__, Sanctuary.__obj_name__, Hidden.__obj_name__,
    Sneak.__obj_name__, Flying.__obj_name__, DetectHidden.__obj_name__,
    DetectInvis.__obj_name__, Silenced.__obj_name__
}
