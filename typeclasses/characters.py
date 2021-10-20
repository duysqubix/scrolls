"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
import copy
import numpy as np
from world.utils.db import search_roomdb
from evennia import DefaultCharacter, EvMenu, TICKER_HANDLER, search_object
from evennia.utils.utils import inherits_from, lazy_property, make_iter

from typeclasses.rooms.rooms import Room
from world.conditions import HolyLight
from world.utils.act import Announce, act
from world.utils.utils import can_see_obj, delete_contents, is_equippable, is_npc, is_obj, is_pc, is_pc_npc, is_wieldable, is_wielded, is_wiz, is_worn, apply_obj_effects, remove_obj_effects
from world.gender import Gender
from world.races import NoRace
from world.attributes import Attribute, VitalAttribute
from world.birthsigns import NoSign
from world.globals import BUILDER_LVL, DEFAULT_PROMPT_STRING, GOD_LVL, IMM_LVL, PROMPT_TOKEN_MAP, Positions, START_LOCATION_VNUM, TICK_HEAL_CHAR, TICK_SAVE_CHAR, WIZ_LVL, WEAR_LOCATIONS
from world.characteristics import CHARACTERISTICS
from world.skills import Skill
from world.storagehandler import StorageHandler
from world.languages import LanguageSkill, VALID_LANGUAGES


class _CalcVitals:
    def __init__(self, level, **kwargs):
        self.level = level
        self.base_mult = 3.0
        for k, v in kwargs.items():
            setattr(self, k, v)

    def calc(self):
        raise NotImplementedError()

    @property
    def base(self):
        return (self.base_mult * np.log2(self.lvl)) * self.lvl

    def __repr__(self):
        return str(self.calc())


class Hp(_CalcVitals):
    def calc(self):
        val = int((self.base + (self.end)) * self.diff_mod)
        return val


class Wp(_CalcVitals):
    def calc(self):
        return int((self.base + ((self.int + self.wp) / 2) * self.diff_mod))


class Sp(_CalcVitals):
    def calc(self):
        return int((self.base + ((self.end + self.agi) / 2) * self.diff_mod))


class LanguageHandler(StorageHandler):
    """
    Stores language skills 
    """
    __attr_name__ = 'languages'

    def init(self) -> None:
        for lang in VALID_LANGUAGES.keys():
            if not getattr(self, lang, None):
                setattr(self, lang, LanguageSkill.untrained)

    def get(self, name, default=None):
        if name == 'common':
            name = 'tamrielic'
        return getattr(self, name, default)

    def clear(self):
        """ resets languages on self to 0.0"""
        for lang in VALID_LANGUAGES.keys():
            langattr = getattr(self, lang, None)
            if not langattr:
                continue
            setattr(self, lang, LanguageSkill.untrained)


class EquipmentHandler:
    """
    Handles equipment based objects that exist in caller.location
    identified by
    """
    _valid_wear_loc = WEAR_LOCATIONS

    def __init__(self, caller):
        self.caller = caller
        self.location = {}
        self.loc_help_msg = {}

        for loc in self._valid_wear_loc:
            self.location[loc.name] = None  # obj

        # now try to find objects in caller.location
        # that are 1) is_equippable and 2)is_worn or 3) is wieldable and 4) is_wielded
        for obj in self.caller.contents:
            if (is_equippable(obj) and is_worn(obj)):
                self.location[obj.db.wear_loc] = obj

            if (is_wieldable(obj) and is_wielded(obj)):
                self.location['wield'] = obj

    def add(self, obj):
        """ 
        add piece of equipment from inventory to and make worn
        include any stat changes and affects to player here
        """
        if self.location[obj.db.wear_loc] is not None:
            self.caller.msg(
                f"You are already wearing something on your {obj.db.wear_loc}")
            return

        obj.db.is_worn = True
        self.location[obj.db.wear_loc] = obj
        act("$n wears $p", True, True, self.caller, obj, None, Announce.ToRoom)
        act("You wear $p", True, True, self.caller, obj, None, Announce.ToChar)
        apply_obj_effects(self.caller, obj)

    def wield(self, obj):
        if self.location['wield'] is not None:
            self.caller.msg("You are already wielding something.")
            return
        obj.db.is_wielded = True
        self.location['wield'] = obj

        act("$n wields $p", True, True, self.caller, obj, None,
            Announce.ToRoom)
        act("You wield $p", True, True, self.caller, obj, None,
            Announce.ToChar)
        apply_obj_effects(self.caller, obj)

    def unwield(self, obj):
        obj.db.is_wielded = False
        self.location['wield'] = None
        act("$n unwields $p", True, True, self.caller, obj, None,
            Announce.ToRoom)
        act("You unwield $p", True, True, self.caller, obj, None,
            Announce.ToChar)
        remove_obj_effects(self.caller, obj)

        return True

    def remove(self, obj):
        """ 
        remove piece of equipment from inventory
        remove any stat changes and affects to player here
        """
        obj.db.is_worn = False
        self.location[obj.db.wear_loc] = None

        act("$n removes $p", True, True, self.caller, obj, None,
            Announce.ToRoom)
        act("You remove $p", True, True, self.caller, obj, None,
            Announce.ToChar)
        remove_obj_effects(self.caller, obj)

        return True


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

    def modify_stat(self, stat_name, by=0):
        _s = self.caller.stats.get(stat_name)
        if _s is None:
            raise ValueError("No stat like that exists to be modified")
        _s.bonus += by
        self.set(stat_name, _s)


class ConditionHandler(StorageHandler):
    __attr_name__ = 'conditions'

    def has(self, condition):
        return True if self.get(condition) is not None else False

    def add(self, *conditions, quiet=False):
        """
        Args:
            conditions: list of condition tuples: [(cls, X, Y),]
        """
        for con in conditions:
            cls, X, Y = con

            c = cls(X, Y)
            # check to see if caller has condition
            if self.has(cls) and c.allow_multi is False:
                # self.caller.msg("you can't be affected by this again")
                return None
            c.at_condition(self.caller)  # fire at condition
            self.set(c)

            if not quiet and (c.__activate_msg__ != ""):
                self.caller.msg(c.__activate_msg__)

    def remove(self, *condition, quiet=False):
        for con in condition:
            cls, x, y = con
            if not self.has(cls):  # trying to remove a non-existant condition
                return True
            c = self.get(cls)
            if c.enabled is True:  # try to end it
                if c.end_condition(self.caller) is False:
                    self.caller.msg(
                        f"try as you might, you are still affected by {cls.__obj_name__}"
                    )
                    return False
            c.after_condition(self.caller)

            match = None
            for _c in self.__getattr__(self.__attr_name__):
                if _c == c:
                    match = _c
                    break

            if match is not None:
                self.__getattr__(self.__attr_name__).remove(match)
                if not quiet and (c.__deactivate_msg__ != ""):
                    self.caller.msg(c.__deactivate_msg__)

    def get(self, condition):
        name = self.__attr_name__
        con_name = condition.__obj_name__
        conditions = self.__getattr__(name)

        if not conditions:
            return None
        cond = [x for x in conditions if x.name == con_name]

        if not cond:
            return None
        cond = cond[0]
        return cond

    def set(self, condition):
        name = self.__attr_name__
        self.__getattr__(name).append(condition)


class TraitHandler(ConditionHandler):
    __attr_name__ = "traits"


class AttrHandler(StorageHandler):
    __attr_name__ = "attrs"

    def update(self):
        self.max_carry()
        self.max_health()
        self.max_magicka()
        self.max_speed()
        self.max_stamina()

    @property
    def base_vital(self):
        level = self.caller.attrs.level.value
        return (1.5 * np.log2(level)) * level

    def change_vital(self, attr_type, by=0, update=True):
        """
        helper function to change current vital value 
        based on max and current value. attr_type supplied must be
        valid key that points to attributes on AttributeHandler, and must
        be a valid VitalAttribute object
        """
        attr = self.__getattr__(attr_type)
        if not inherits_from(attr, 'world.attributes.VitalAttribute'):
            raise NotImplementedError(
                'change_vital function doesnt support changing attribute that are NOT VitalAttributes'
            )

        if attr.cur == attr.max:
            return

        cur = attr.cur

        cur += int((by * attr.rate))  # apply rate
        if cur < 0:
            cur = 0
        if cur > attr.max:
            cur = attr.max
        attr.cur = cur
        self.__setattr__(attr_type, attr)
        if update:
            self.update()

    def modify_vital(self, attr_type, by=0):
        """
        same as change_vital except  adds it to modifier list
        attr_type must be a vald key on AttributeHandler
        """

        attr = self.__getattr__(attr_type)
        if not inherits_from(attr, 'world.attributes.VitalAttribute'):
            raise NotImplementedError(
                'modify_vital function doesnt support changing attribute that are NOT VitalAttributes'
            )

        #
        # Nifty piece of code  here, instead of tracking individual
        # objects that modify vitals, instead I turned it into a math
        # game. If your mod list looks like this:
        #
        # mod = [1,1,-2,5], your a cum modifier of 5
        #
        # when you add a modifer to the list, instead of it growing
        # forever, it will first try to find the oppositve value
        # and attempt to remove that, if it can't find it, it will a
        # add it. For example
        #
        # health_mod = [2,2,-3,5,10] (16)
        # modify_vital('health', by=3) # adding three to modifer
        #
        # results would be:
        #
        # health_mod = [2,2,5,10] (19)
        # it found a opposite of 3 (-3)
        # and removed that.

        # modify_vital('health', by=-10) # deduct 10 from mod
        # health_mod = [2,2,5] (9)

        # doing it again though: modify_vital('health', by=-10)
        # health_mod = [2,2,5,-10] (-1)
        #
        #

        if by != 0:
            # attempt to remove a positive equiv
            # mod, if it doesn't exist add it
            tmp = -by
            try:
                idx = attr.mod.index(tmp)
                attr.mod.remove(attr.mod[idx])
            except ValueError:
                # it doesn't exist, just add it to list
                attr.mod.append(by)
        self.__setattr__(attr_type, attr)
        self.update()

    def max_health(self):
        health = self.base_vital * np.log(self.caller.stats.end.base)
        tot = int(health) + self.health.mods

        self.health.max = max(tot, 3)
        return max(tot, 3)

    def max_stamina(self):
        end = self.caller.stats.end.base
        agi = self.caller.stats.agi.base
        stamina = self.base_vital * np.log(((end + agi) / 2))
        tot = int(stamina) + self.stamina.mods

        self.stamina.max = max(tot, 3)
        return max(tot, 3)

    def max_magicka(self):
        wp = self.caller.stats.wp.base
        int_ = self.caller.stats.int.base
        magicka = self.base_vital * np.log((wp + int_) / 2)
        tot = int(magicka) + self.magicka.mods + 20

        self.magicka.max = max(tot, 3)
        return max(tot, 3)

    def max_speed(self):
        sb = self.caller.stats.str.bonus
        ab = self.caller.stats.agi.bonus
        speed = sb + (2 * ab) + 20

        tot = speed + self.speed.mods
        self.speed.max = tot
        return tot

    def max_carry(self):
        # carry rating
        str = self.caller.stats.str.collect()
        end = self.caller.stats.end.collect()
        carry = ((0.75 * str) + (0.25 * end)) + 50

        tot = int(carry) + self.carry.mods
        self.carry.max = tot
        return tot


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
    def at_say(self,
               message,
               msg_self=None,
               msg_location=None,
               receivers=None,
               msg_receivers=None,
               **kwargs):
        mapping = {
            'self':
            "You",
            'object':
            self.name.capitalize()
            if is_pc(self) else self.db.sdesc.capitalize()
        }
        msg_self = "{self} say, |c{speech}|n"
        msg_location = "{object} says, |c{speech}|n"
        msg_receivers = "{object} tells you, |c{speech}|n"
        super().at_say(message=message,
                       msg_self=msg_self,
                       receivers=receivers,
                       msg_location=msg_location,
                       msg_receivers=msg_receivers,
                       mapping=mapping,
                       **kwargs)

    def announce_move_from(self,
                           destination,
                           msg=None,
                           mapping=None,
                           **kwargs):
        pass

    def announce_move_to(self,
                         source_location,
                         msg=None,
                         mapping=None,
                         **kwargs):
        pass

    def at_after_move(self, src_location):
        self.execute_cmd("look")

    def at_post_puppet(self, **kwargs):

        # here we can check to see if this is the first time logging in.
        if self.attributes.has('new_character'):

            # set some vital things, if this is super users first login
            if self.is_superuser:
                self.attrs.level.value = GOD_LVL

                # load db into global scripts
                self.execute_cmd('dbload all')

                # iterate through all rooms and create them if they dont' exist
                rvnums = search_roomdb('all', return_keys=True)
                for rvnum in rvnums:
                    self.execute_cmd(f'goto {rvnum}')

                self.execute_cmd('goto %s' % START_LOCATION_VNUM)
            #enter the chargen state
            EvMenu(self,
                   "world.chargen.gen",
                   startnode="pick_race",
                   cmdset_mergetype='Replace',
                   cmdset_priority=1,
                   auto_quit=False)
            self.attributes.remove('new_character')

        ############### Non-Persistent Tickers ####################
        TICKER_HANDLER.add(interval=TICK_HEAL_CHAR,
                           callback=self.tick_heal_player,
                           idstring=f"tick_heal_{self.name}",
                           persistent=False)

        TICKER_HANDLER.add(interval=TICK_SAVE_CHAR,
                           callback=self.save_character,
                           idstring=f"tick_save_{self.name}",
                           persistent=False)
        ###########################################################
        self.msg(f"\nYou become |c{self.name.capitalize()}|n")
        self.execute_cmd('look')

    def save_character(self):
        self.db.stats = dict(self.db.stats)
        self.db.skills = dict(self.db.skills)
        self.db.conditions = dict(self.db.conditions)
        self.db.traits = dict(self.db.traits)
        self.db.attrs = dict(self.db.attrs)

        try:
            self.msg(prompt=self.get_prompt())
        except:
            pass

    def at_pre_unpuppet(self):
        self.save_character()

    def at_server_reload(self):
        self.save_character()

    def at_server_shutdown(self):
        self.save_character()

    def at_after_move(self, src, **kwargs):
        self.execute_cmd('look')

    def at_cmdset_get(self, **kwargs):

        if self.db.attrs:  # does this  just on character typeclasses
            level = self.attrs.level.value
            if level >= BUILDER_LVL:
                if not self.cmdset.has(
                        'commands.default_cmdsets.BuilderCmdSet'):
                    self.cmdset.add('commands.default_cmdsets.BuilderCmdSet')
                    self.msg("builder_cmds added")
            if level >= IMM_LVL:
                imm_cmdset = 'commands.default_cmdsets.ImmCmdSet'
                if not self.cmdset.has(imm_cmdset):
                    self.cmdset.add(imm_cmdset)
                    self.msg("immortal_cmds added")
            if level >= WIZ_LVL:
                wiz_cmdset = 'commands.default_cmdsets.WizCmdSet'
                if not self.cmdset.has(wiz_cmdset):
                    self.cmdset.add(wiz_cmdset)
                    self.msg("wizard_cmds added")
            if level >= GOD_LVL:
                god_cmdset = 'commands.default_cmdsets.GodCmdSet'
                if not self.cmdset.has(god_cmdset):
                    self.cmdset.add(god_cmdset)
                    self.msg("god_cmds added")

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

    @lazy_property
    def traits(self):
        return TraitHandler(self)

    @lazy_property
    def equipment(self):
        return EquipmentHandler(self)

    @lazy_property
    def languages(self):
        return LanguageHandler(self)

    def full_title(self):
        return f"{self.name.capitalize()}{self.attrs.title.value}"        

    def get_prompt(self):

        if not self.db.prompt:
            self.db.prompt = DEFAULT_PROMPT_STRING

        self.attrs.update()
        hp = self.attrs.health
        mg = self.attrs.magicka
        st = self.attrs.stamina
        sp = self.attrs.speed
        ca = self.attrs.carry
        prompt = f"\n\n{self.db.prompt}"

        if is_wiz(self) and self.conditions.has(HolyLight):
            prompt += "(|wholy|ylight|n)"


        for token, py_statement in PROMPT_TOKEN_MAP.items():
            prompt = prompt.replace(token, str(eval(py_statement)))

        prompt += " >"
        #prompt += f"HP:{hp.cur}/{hp.max} MG:{mg.cur}/{mg.max} ST:{st.cur}/{st.max} SP:{sp.cur}/{sp.max} CR:{ca.cur}/{ca.max} > "
        return prompt

    def full_restore(self):
        self.attrs.update()
        self.attrs.health.cur = self.attrs.health.max
        self.attrs.magicka.cur = self.attrs.magicka.max
        self.attrs.speed.cur = self.attrs.speed.max
        self.attrs.stamina.cur = self.attrs.stamina.max

    def tick_heal_player(self):
        # called by global ticker  handler
        # heals the player based on vitals restore rate
        # up until the player is fully healed.
        # then remove subscription until damaged again.

        # heal stats based on level
        level = self.attrs.level.value
        amnt = 0.17588 * level + 5

        #health
        self.attrs.change_vital('health', by=amnt, update=False)
        self.attrs.change_vital('magicka', by=amnt, update=False)
        self.attrs.change_vital('speed', by=amnt, update=False)
        self.attrs.change_vital('stamina', by=amnt, update=True)

    def clear_inventory(self):
        """ recurively delete all objs within self.contents """
        delete_contents(self)

    def location_contents(self):
        objs = []
        for obj in self.location.contents:
            if is_obj(obj):
                objs.append(obj)
        return objs

    def debug_msg(self, *args):
        x = tuple(args)
        self.msg(str(x))

    def add_attr(self, name, value, is_vital=False):
        if not self.attributes.has('attrs'):
            self.attributes.add('attrs', dict())

        if is_vital:
            self.db.attrs[name] = VitalAttribute(name=name, value=value)
        else:
            self.db.attrs[name] = Attribute(name=name, value=value)

    def at_object_creation(self):
        self.db.look_index = 0
        self.db.new_character = True  # used for character generation
        self.db.name = self.name
        self.db.attrs = {}
        self.db.stats = {}
        self.db.skills = {}
        self.db.languages = {}
        self.db.conditions = {'conditions': []}
        self.db.traits = {'traits': []}
        self.db.stats = copy.deepcopy(CHARACTERISTICS)
        self.db.is_npc = False
        self.db.is_pc = True

        # level
        level = GOD_LVL if self.is_superuser else 1
        # attributes
        self.add_attr('gender', Gender.NoGender)
        self.add_attr('exp', 0)
        self.add_attr('title', ", the new blood.")
        self.add_attr('level', level)
        self.add_attr('race', NoRace())
        self.add_attr('immunity', {
            'poison': [],
            'disease': [],
            'conditions': []
        })
        self.add_attr('AR', 0),
        self.add_attr('MAR', 0)
        self.add_attr('birthsign', NoSign())
        self.add_attr('position', Positions.Standing)
        self.add_attr('health', None, is_vital=True)
        self.add_attr('magicka', None, is_vital=True)
        self.add_attr('stamina', None, is_vital=True)
        self.add_attr('speed', None, is_vital=True)
        self.add_attr('carry', None, is_vital=True)

        # set new starting location here
        start_loc = search_object('2', typeclass=Room)
        if start_loc:
            self.location = start_loc[0]
