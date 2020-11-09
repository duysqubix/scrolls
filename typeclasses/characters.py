"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
import copy
from world.birthsigns import NoSign
from evennia import DefaultCharacter
from world.globals import GOD_LVL, WIZ_LVL
from world.characteristics import CHARACTERISTICS
from world.skills import Skill
from evennia.utils.utils import lazy_property
from world.storagehandler import StorageHandler
from evennia.utils.evmenu import EvMenu


class SkillHandler(StorageHandler):
    __attr_name__ = "skills"

    def __getitem__(self, key):
        if key in self.__dict__.keys():
            return self.__dict__[key]
        return None

    def add(self, skill: Skill):
        if not isinstance(skill, Skill):
            raise ValueError('not a valid skill object')
        setattr(self, skill.name, skill)


class StatHandler(StorageHandler):
    __attr_name__ = "stats"


class ConditionHandler(StorageHandler):
    __attr_name__ = 'conditions'

    def has(self, condition):
        return True if self.get(condition) is not None else False

    def add(self, condition, X=None, **kwargs):

        # check to see if caller has condition
        if not self.has(condition):
            con = condition(X=X)  # initialize condition
            con.at_condition(self.caller)  # fire at condition
            # add it to list of conditions stored on handler
            self.set(con)

    def remove(self, condition):
        if not self.has(
                condition):  # trying to remove a non-existant condition
            return True
        con = self.get(condition)
        if con.enabled is True:  # try to end it
            if con.end_condition(self.caller) is False:
                self.caller.msg(
                    f"try as you might, you are still affected by {con.__conditionname__}"
                )
                return False
        con.after_condition(self.caller)
        del self.caller.db.conditions[con.name]

    def get(self, condition):
        print(condition, type(condition))
        name = condition.__conditionname__
        try:
            return self.__getattr__(name)
        except KeyError:
            return None

    def set(self, condition):
        name = condition.__conditionname__
        value = condition
        self.__setattr__(name, value)


class AttrHandler(StorageHandler):
    __attr_name__ = "attrs"

    @property
    def max_health(self):
        return self.caller.stats.end.base // 2 + 1

    @property
    def max_stamina(self):
        return self.caller.stats.end.bonus

    @property
    def max_magicka(self):
        return self.caller.stats.int.base

    @property
    def max_speed(self):
        sb = self.caller.stats.str.bonus
        ab = self.caller.stats.agi.bonus
        return sb + (2 * ab)

    @property
    def max_carry(self):
        # carry rating
        sb = self.caller.stats.str.bonus
        eb = self.caller.stats.end.bonus

        return (4 * sb) + (2 * eb)

    @property
    def max_luck(self):
        return self.caller.stats.lck.bonus

    def init(self):

        # linguistics
        self.linguistics = self.caller.stats.int.bonus // 2 + 1

        # initiative
        ab = self.caller.stats.agi.bonus
        ib = self.caller.stats.int.bonus
        pcb = self.caller.stats.prs.bonus
        self.initiative = ab + ib + pcb

        # current health, magicka, stamina
        self.health = self.max_health
        self.magicka = self.max_magicka
        self.stamina = self.max_stamina
        self.speed = self.max_speed
        self.carry = self.max_carry


class Character(DefaultCharacter):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_after_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """
    @lazy_property
    def stats(self):
        return StatHandler(self)

    @lazy_property
    def attrs(self):
        return AttrHandler(self)

    @lazy_property
    def skills(self):
        return SkillHandler(self)

    @lazy_property
    def conditions(self):
        return ConditionHandler(self)

    @property
    def is_pc(self):
        return True

    def at_object_creation(self):

        # characteristics
        self.db.stats = copy.deepcopy(CHARACTERISTICS)

        # level
        level = None
        if self.is_superuser and self.id == 1:
            level = GOD_LVL

        elif self.is_superuser:
            level = WIZ_LVL
        else:
            level = 1
        # attributes
        self.db.attrs = {
            'exp': 0,
            'level': level,
            'birthsign': NoSign(),
            'race': 'none'
        }

        _ = self.attrs
        _ = self.stats
        _ = self.skills
        _ = self.conditions
        # enter the chargen state
        # EvMenu(self,
        #        "world.char_gen",
        #        startnode="pick_race",
        #        cmdset_mergetype='Replace',
        #        cmdset_priority=1,
        #        auto_quit=False)
