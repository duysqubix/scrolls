"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
import copy
from world.attributes import Attribute, VitalAttribute
from world.birthsigns import NoSign
from evennia import DefaultCharacter
from world.globals import GOD_LVL, WIZ_LVL
from world.characteristics import CHARACTERISTICS
from world.skills import Skill
from evennia.utils.utils import inherits_from, lazy_property, make_iter
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
        condition = make_iter(condition)

        for con in condition:
            # check to see if caller has condition
            if not self.has(con):
                c = con(caller_id=self.caller.id, X=X)  # initialize condition
                c.at_condition()  # fire at condition
                # add it to list of conditions stored on handler
                #TODO: need to handle if condition is already set
                self.set(c)

    def remove(self, condition):
        condition = make_iter(condition)

        for con in condition:
            if not self.has(con):  # trying to remove a non-existant condition
                return True
            c = self.get(con)
            if c.enabled is True:  # try to end it
                if c.end_condition() is False:
                    self.caller.msg(
                        f"try as you might, you are still affected by {con.__conditionname__}"
                    )
                    return False
            c.after_condition()
            del self.caller.db.conditions[c.name]

    def get(self, condition):
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

    def update(self):
        self.max_carry()
        self.max_health()
        self.max_magicka()
        self.max_speed()
        self.max_stamina()

    def change_vital(self, attr_type, by=0):
        """
        helper function to change current vital value 
        based on max and current value. attr_type supplied must be
        valid key that points to attributes on AttributeHandler, and must
        be a valid VitalAttribute object
        """
        attr = self.__dict__[attr_type]
        if not inherits_from(attr, 'world.attributes.VitalAttribute'):
            raise NotImplementedError(
                'change_vital function doesnt support changing attribute that are NOT VitalAttributes'
            )
        cur = attr.cur
        cur += by
        if cur < 0:
            cu = 0
        if cur > attr.max:
            cur = attr.max

        self.__dict__[attr_type].cur = cur

    def max_health(self):
        health = (self.caller.stats.end.base // 2 + 1)
        self.health.max = health
        return health + self.health.mods

    def max_stamina(self):
        stamina = self.caller.stats.end.bonus
        self.stamina.max = stamina
        return stamina + self.stamina.mods

    def max_magicka(self):
        magicka = self.caller.stats.int.base
        self.magicka.max = magicka
        return magicka + self.magicka.mods

    def max_speed(self):
        sb = self.caller.stats.str.bonus
        ab = self.caller.stats.agi.bonus
        speed = sb + (2 * ab)
        self.speed.max = speed
        return speed + self.speed.mods

    def max_carry(self):
        # carry rating
        sb = self.caller.stats.str.bonus
        eb = self.caller.stats.end.bonus
        carry = ((4 * sb) + (2 * eb))
        self.carry.max = carry
        return carry + self.carry.mods


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
    @property
    def is_pc(self):
        return True

    @lazy_property
    def attrs(self):
        return AttrHandler(self)

    @lazy_property
    def skills(self):
        return SkillHandler(self)

    @lazy_property
    def stats(self):
        return StatHandler(self)

    @lazy_property
    def conditions(self):
        return ConditionHandler(self)

    def at_object_creation(self):
        self.db.attrs = {}
        self.db.stats = {}
        self.db.skills = {}
        self.db.conditions = {}

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
            'exp':
            Attribute('exp', 0),
            'level':
            Attribute('level', level),
            'race':
            Attribute('race', 'none'),
            'immunity':
            Attribute('immunity', {
                'poison': [],
                'disease': [],
                'conditions': []
            }),
            'birthsign':
            Attribute('birthsign', NoSign()),
            'action_points':
            Attribute('action_points', 3),
            'health':
            VitalAttribute('health'),  # cur/max/mod_max/recover
            'magicka':
            VitalAttribute('magicka'),
            'stamina':
            VitalAttribute('stamina'),
            'speed':
            VitalAttribute('speed'),
            'carry':
            VitalAttribute('carry'),
        }

        # _ = self.traits
        # enter the chargen state
        # EvMenu(self,
        #        "world.char_gen",
        #        startnode="pick_race",
        #        cmdset_mergetype='Replace',
        #        cmdset_priority=1,
        #        auto_quit=False)
