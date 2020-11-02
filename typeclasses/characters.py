"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter
from world.globals import GOD_LVL, WIZ_LVL, Size
from world.characteristics import CHARACTERISTICS
from world.skills import Skill
from evennia.utils.utils import lazy_property
from world.storagehandler import StorageHandler

class SkillHandler(StorageHandler):
    __attr_name__ = "skills"

    def __getitem__(self, key):
        if key in self.__dict__.keys():
            return self.__dict__[key]
        return None

    def add(self, skill: Skill):
        setattr(self, skill.name, skill)

class StatHandler(StorageHandler):
    __attr_name__ = "characteristics"


class AttrHandler(StorageHandler):
    __attr_name__ = "attrs"

    @property
    def max_health(self):
        end = self.caller.stats.end.value
        return end // 2 + 1

    @property
    def stamina(self):
        return self.caller.stats.end.bonus

    @property
    def magicka(self):
        return self.caller.stats.int.value

    @property
    def linguistics(self):
        return self.caller.stats.int.bonus // 2 + 1

    @property
    def initiative(self):
        ab = self.caller.stats.agi.bonus
        ib = self.caller.stats.int.bonus
        pcb = self.caller.stats.prs.bonus
        return ab + ib + pcb

    @property
    def speed(self):
        sb = self.caller.stats.str.bonus
        ab = self.caller.stats.agi.bonus
        return sb + (2 * ab)

    @property
    def carry_rating(self):
        sb = self.caller.stats.str.bonus
        eb = self.caller.stats.end.bonus
        return (4 * sb) + (2 * eb)

    @property
    def luck(self):
        return self.caller.stats.lck.bonus


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

    def at_object_creation(self):



        # characteristics
        stats_x = [x.short for x in CHARACTERISTICS]
        stats_y = CHARACTERISTICS
        self.db.characteristics = dict(zip(stats_x, stats_y))


        # level
        level = None
        if self.db.superuser and self.id == 1:
            level = GOD_LVL

        elif self.db.superuser:
            level = WIZ_LVL
        else:
            level = 1
        # attributes
        self.db.attrs = {'action_points': 3, 'exp': 0, 'level': level}

        # skills
        self.db.skills = dict()