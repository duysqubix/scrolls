"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia import DefaultCharacter
from world.globals import GOD_LVL, WIZ_LVL, Size
from evennia.utils.utils import lazy_property


class StorageHandler:
    __attr_name__ = ""

    def __init__(self, caller):
        self.caller = caller
        self.integrity_check()

    def __setattr__(self, name, value):
        self.__dict__[name] = value
        attr = self.caller.attributes.get(self.__attr_name__, dict())
        attr[name] = value

    def all(self):
        return [x for x in self.__dict__.keys() if x not in ['caller']]

    def integrity_check(self):
        for k, v in self.caller.attributes.get(self.__attr_name__,
                                               dict()).items():
            setattr(self, k, v)


class SkillHandler(StorageHandler):
    __attr_name__ = "skills"

    def __getitem__(self, key):
        if key in self.__dict__.keys():
            return self.__dict__[key]
        return None


class Stat:
    def __init__(self, name):
        self.name = name
        self.value = 0


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
        return self.caller.stats.eb.value

    @property
    def magicka(self):
        return self.caller.stats.int.value

    @property
    def linguistics(self):
        return self.caller.stats.ib.value // 2 + 1

    @property
    def initiative(self):
        ab = self.caller.stats.ab.value
        ib = self.caller.stats.ib.value
        pcb = self.caller.stats.pcb.value
        return ab + ib + pcb

    @property
    def speed(self):
        sb = self.caller.stats.sb.value
        ab = self.caller.stats.ab.value
        return sb + (2 * ab)

    @property
    def carry_rating(self):
        sb = self.caller.stats.sb.value
        eb = self.caller.stats.eb.value
        return (4 * sb) + (2 * eb)

    @property
    def luck(self):
        return self.caller.stats.lkb.value


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

        # level
        if self.db.level is None:
            if self.is_superuser and self.id == 1:
                self.db.level = GOD_LVL

            elif self.is_superuser:
                self.db.level = WIZ_LVL
            else:
                self.db.level = 1

        # characteristics
        stats_x = [
            'str', 'sb', 'end', 'eb', 'agi', 'ab', 'int', 'ib', 'wp', 'wb',
            'prc', 'pcb', 'prs', 'psb', 'lck', 'lkb'
        ]
        stats_y = [Stat(x) for x in stats_x]
        self.db.characteristics = dict(zip(stats_x, stats_y))

        # attributes
        self.db.attrs = {'size': Size.standard(), 'action_points': 3, 'exp': 0}

        # skills
        # skills are stored as {name: vnum_skill}
        self.db.skills = {}