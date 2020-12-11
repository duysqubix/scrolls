from enum import IntEnum
import numpy as np

from evennia import CmdSet, Command, EvEditor, GLOBAL_SCRIPTS
from evennia.commands.default.help import CmdHelp
from evennia.utils.utils import crop, list_to_string, wrap

from evennia.contrib.dice import roll_dice

from world.globals import DAM_TYPES, DEFAULT_MOB_STRUCT, MAX_LEVEL, MIN_LEVEL, Positions, Size
from world.edit.model import _EditMode
from typeclasses.mobs.mob import VALID_MOB_APPLIES, VALID_MOB_FLAGS
from world.utils.utils import mxp_string

_MEDIT_PROMPT = "(|ymedit|n)"


class MEditMode(_EditMode):
    __cname__ = 'mob'
    __db__ = GLOBAL_SCRIPTS.mobdb
    __prompt__ = _MEDIT_PROMPT
    __default_struct__ = DEFAULT_MOB_STRUCT

    def init(self):
        assigned_zone = self.caller.attributes.get('assigned_zone')
        if not assigned_zone:
            raise Exception(
                "user should not be allowed in the first place with medit without a valid zone assigned"
            )

        if self.obj['zone'] == 'null':
            self.obj['zone'] = assigned_zone

        self.save(override=True)

    def save(self, override=False, bypass_checks=False):
        if (self.orig_obj != self.obj) or override:

            # custom field checks here
            if not bypass_checks:
                ##### fields #####
                # key
                # sdesc
                # ldesc
                # edesc
                # position
                # attack
                # flags
                # applies
                # level
                # self.obj['level'] = int(self.obj['level'])
                # stats
                pass

            self.db.vnum[self.vnum] = self.obj
            self.caller.msg('mob saved')

    def summarize(self):
        s = self.obj['stats']

        dam_min = s['dam_size'] + s['dam_mod']
        dam_max = (s['dam_size'] * s['dam_num']) + s['dam_mod']
        dam_avg = int(((s['dam_size'] + 1) / 2) * s['dam_num']) + s['dam_mod']
        msg = f"""
********Mob Summary*******

|GVNUM|n: [{self.vnum}]      |GZONE|n:[|r{self.obj['zone']}|n]

|Gkey|n    : {self.obj['key']}
|Gsdesc|n  : {self.obj['sdesc']}
|Gldesc|n  : 
{crop(self.obj['ldesc'])}

|Gedesc|n    : 
{crop(self.obj['edesc'])}

|Gposition|n : {self.obj['position']}
|Gattack|n   : {self.obj['attack']}
|Gapplies|n  : {list_to_string(self.obj['applies'])}
|Gflags|n    : {list_to_string(self.obj['flags'])}

|GLevel|n: {self.obj['level']}  
|GSize|n: {self.obj['size']:<5}
|r----------------|rStats|R---------------------|n

|GStr|n: {s['str']:<3}  |GWp |n: {s['wp']:<3}    |GHP|n: {s['hp']:<3}   
|GEnd|n: {s['end']:<3}  |GPrc|n: {s['prc']:<3}    |GMP|n: {s['mp']:<3}   
|GAgi|n: {s['agi']:<3}  |GPrs|n: {s['prs']:<3}    |GSP|n: {s['sp']:<3}   
|GInt|n: {s['int']:<3}  |GLck|n: {s['lck']:<3}    |GAR|n: {s['ar']:<3}

|Ghit_roll |n: {s['hit_roll']:<5}


Damage Statistics:
---------------------------------
|Gdam_num|n: {s['dam_num']}
|Gdam_size|n: {s['dam_size']}
|Gdam_mod |n: {s['dam_mod']:<4} (|Y{dam_min}|n to |Y{dam_max}|n) (|G{dam_avg}|n)
---------------------------------

"""

        self.caller.msg(msg)


class MEditCmdSet(CmdSet):
    key = "MEditMode"

    mergetype = "Replace"

    def at_cmdset_creation(self):
        self.add(Exit())
        self.add(Look())
        self.add(CmdHelp())
        self.add(Set())
        self.add(AutoLevel())


class MEditCommand(Command):
    def at_post_cmd(self):
        self.caller.msg(prompt=_MEDIT_PROMPT)


class AutoLevel(Command):
    """
    Sets stats for character based on 
    human friendly language..

    This uses a random dice roller from a base stat of
    25 in all stats. This represents the easy category.
    Calling the other level types, adds a direct modifier to 
    the base in multiples of 2.

    Meaning that: 
        a hard mob is 4x harder than a medium, which is 16x harder than an easy, and 64x harder than a wimpy


    Usage:
        autolevel [wimpy/easy/medium/hard/insane/chaotic]
    """

    _base_multiplier = 2
    _base_stat = 0
    _base_stat_mult = 1.5
    _mob_difficulty = 2

    key = 'autolevel'
    aliases = ['auto']

    def func(self):
        ch = self.caller
        args = self.args.strip()
        obj = ch.ndb._medit.obj

        valid_attrs = ('str', 'end', 'agi', 'int', 'wp', 'prc', 'prs', 'lck')

        if not args:
            level = 'easy'
        else:
            if args not in MobDifficulty.members():
                ch.msg(
                    f"That is not a valid toughness, try {mxp_string('help autolevel', 'help autolevel')})"
                )
                return
            level = args

        dice = np.vectorize(lambda x: x + roll_dice(2, 5))
        base_stats = np.full((8, ), fill_value=self._base_stat, dtype=np.int64)

        base_stats = dice(base_stats)

        members = MobDifficulty.members(return_dict=True)
        seed = {
            "base_mult": self._base_stat_mult,
            "olvl": obj['level'],
            "diff_mult": self._mob_difficulty,
            "diff": members[level]
        }

        for idx, name in enumerate(valid_attrs):
            obj['stats'][name] = base_stats[idx]

        seed.update(obj['stats'])
        auto = AutoMobScaling(**seed)
        obj['stats']['hp'] = auto.calc_hp()
        obj['stats']['sp'] = auto.calc_sp()
        obj['stats']['mp'] = auto.calc_mp()

        #TODO: find a good wayto auto set dam_roll based on level
        # obj['stats']['dam_num'] = num_dice
        num, size = auto.calc_dam()
        _max = int(num * size)
        obj['stats']['dam_num'] = num
        obj['stats']['dam_size'] = size
        obj['stats']['hit_roll'] = auto.calc_hit()

        ch.msg(f"mob autoleveled on {level}")


class Set(MEditCommand):
    """
    Sets various items on currently editting object.
    
    Usage:
        set <field> <params>
    """
    key = 'set'

    valid_obj_attributes = list(DEFAULT_MOB_STRUCT.keys())

    def func(self):
        ch = self.caller
        args = self.args.strip().split()
        obj = ch.ndb._medit.obj
        if not args:
            keywords = "|n\n*|c".join(self.valid_obj_attributes)
            ch.msg(
                f'you must provide one of the valid keywords.\n*|c{keywords}')
            return

        keyword = args[0].lower()
        set_str = f"{keyword} set"

        if keyword not in self.valid_obj_attributes:
            ch.msg("that obj attribute doesn't exist.")
            return

        if keyword in ('key', 'sdesc', 'edesc', 'ldesc'):
            # keyword is key, sdesc, ldesc, adesc
            if len(args) > 1:
                # here the user set the value of the supplied keyword
                # directly in the field, set it and return
                obj[keyword] = " ".join(args[1:]).strip()
                ch.msg(set_str)
            else:
                # open eveditor
                def save_func(_caller, buffer):
                    obj[keyword] = buffer
                    ch.msg(set_str)

                _ = EvEditor(ch,
                             loadfunc=(lambda _x: obj[keyword]),
                             savefunc=save_func)
        elif keyword == 'level':
            if len(args) > 1:
                try:
                    level = int(args[1].strip())
                except:
                    ch.msg("level must be a valid number")
                    return
                obj[keyword] = level
                ch.msg(set_str)
                return
            else:
                # reset level
                obj[keyword] = 0
                ch.msg(set_str)
                return
        elif keyword == 'position':
            if len(args) > 1:
                selected_position = args[1].strip()
                if selected_position not in Positions.members():
                    ch.msg("That is not a valid position")
                    return

                obj[keyword] = selected_position
                ch.msg(set_str)
            else:
                # no position provided, show available positions
                positions = Positions.members()
                table = self.styled_table("Positions")

                for pos in positions:
                    table.add_row(pos)
                ch.msg(table)
                return

        elif keyword == 'attack':
            dam_types = list()
            _ = [dam_types.extend(x) for x in DAM_TYPES.values()]
            if len(args) > 1:
                selected_attack = args[1].strip()
                if selected_attack not in dam_types:
                    ch.msg("That is not a valid attack type")
                    return

                obj[keyword] = selected_attack
                ch.msg(set_str)
                return
            else:
                # show all attack types
                table = self.styled_table("Attack Types")
                dam_types = list_to_string(sorted(dam_types))
                table.add_row(wrap(dam_types, width=50))

                ch.msg(str(table))
                return

        elif keyword == "flags":
            if len(args) > 1:
                selected_flags = [x.strip() for x in args[1:]]
                for flag in selected_flags:
                    if flag == 'clear':
                        obj[keyword].clear()
                        ch.msg("flags cleared")
                        return
                    if flag not in VALID_MOB_FLAGS:
                        ch.msg("That is not a valid npc flag")
                        continue

                    if flag in obj[keyword]:
                        ch.msg('removing flag')
                        obj[keyword].remove(flag)
                    else:
                        obj[keyword].append(flag)
                        ch.msg(set_str)
                return
            else:
                # all flags
                table = self.styled_table("Available NPC Flags")
                flags = list_to_string(VALID_MOB_FLAGS)

                table.add_row(wrap(flags, width=50))
                ch.msg(table)
                return

        elif keyword == 'applies':
            if len(args) > 1:
                selected_applies = [x.strip() for x in args[1:]]
                for apply in selected_applies:
                    if apply == 'clear':
                        obj[keyword].clear()
                        ch.msg("affects cleared")
                        return
                    if apply not in VALID_MOB_APPLIES:
                        ch.msg("That is not a valid npc affect")
                        continue

                    if apply in obj[keyword]:
                        ch.msg('removing affect')
                        obj[keyword].remove(apply)
                    else:
                        obj[keyword].append(apply)
                        ch.msg(set_str)
                return
            else:
                # list all available (conditions)
                table = self.styled_table("Available NPC Conditions")
                affects = list_to_string(sorted(VALID_MOB_APPLIES))
                table.add_row(wrap(affects, width=50))
                ch.msg(table)
                return
        elif keyword == 'size':
            if len(args) > 1:
                size = args[1].strip().lower()
                if size.capitalize() not in Size.members():
                    ch.msg("not a valid size")
                    return
                obj[keyword] = size
                ch.msg(set_str)
            else:
                # list all sizes
                table = self.styled_table("Available NPC Sizes")
                sizes = list_to_string(Size.members())
                table.add_row(wrap(sizes, width=50))
                ch.msg(table)
                return
        elif keyword == 'stats':
            if len(args) > 2:
                stat, value = args[1].strip(), args[2].strip()
                if stat not in obj[keyword].keys():
                    ch.msg("Not a valid stat")
                    return
                try:
                    value = int(value)
                except ValueError:
                    ch.msg("stat values must be a valid number")
                    return

                obj[keyword][stat] = value
                ch.msg(f"set {stat}")
            else:
                # show available stats
                table = self.styled_table("Available NPC Settable Stats")
                stats = sorted(list(obj[keyword].keys()))
                table.add_row(wrap(list_to_string(stats), width=50))
                ch.msg(table)
                return


class Look(MEditCommand):
    """
    view currently editing mobs main stats

    Usage:
        look
    """
    key = "look"
    aliases = ['l', 'ls']

    def func(self):
        ch = self.caller
        ch.ndb._medit.summarize()


class Exit(MEditCommand):
    """
    Exit medit.

    Usage:
        exit
    """
    key = "exit"

    def func(self):
        ch = self.caller
        ch.cmdset.remove('world.edit.medit.MEditCmdSet')
        try:
            b = bool(eval(self.args.strip().capitalize()))
            ch.ndb._medit.save(override=b, bypass_checks=False)
            del ch.ndb._medit
        except:
            ch.ndb._medit.save(override=False, bypass_checks=False)
            del ch.ndb._medit


class MobDifficulty(IntEnum):
    wimpy = 0
    easy = 1
    medium = 2
    hard = 3
    insane = 4
    chaotic = 5

    def members(return_dict=False):
        if return_dict:
            return {
                k.lower(): v
                for k, v, in MobDifficulty._member_map_.items()
            }
        return list(reversed(MobDifficulty._member_map_.keys()))

    def next(self):
        value = self.value + 1
        if value > MobDifficulty.chaotic.value:
            return self

        return MobDifficulty(value)


class AutoMobScaling:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def base(self):
        return (self.base_mult * np.log2(self.olvl)) * self.olvl

    @property
    def diff_mod(self):
        return self.diff_mult**(self.diff.value - 1)

    def __repr__(self):
        return str(self.calc())

    def translate(self, value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin

        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)

        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)

    def calc_hp(self):
        val = int((self.base * np.log(self.end)) * self.diff_mod)
        return max(val, 3)

    def calc_mp(self):
        val = int((self.base * np.log(
            (self.int + self.wp) / 2)) * self.diff_mod)
        return max(val, 3)

    def calc_sp(self):
        val = int((self.base * np.log(
            (self.end + self.agi) / 2)) * self.diff_mod)
        return max(val, 3)

    def calc_dam(self):
        """returns tuple of dice roller
        num, size, mod, (avg)
        ex: [num]D[size] + mod
        """
        old_min = MobDifficulty.wimpy.value
        old_max = MobDifficulty.chaotic.value
        avg = self.calc_hp() / self.translate(
            self.diff.value, old_min, old_max, old_max + 1, old_min + 1)
        num = max(1, int(avg * 1.1))

        vals = []
        threshold = 3
        while not vals:
            for x in range(1, 200):  # x
                for y in range(1, 200):  # y
                    tavg = int((((y + 1) / 2) * x))
                    if abs(tavg - num) < threshold:
                        vals.append((x, y))
            threshold += 10
        v = None
        mwp = len(vals) // 2
        if vals:
            v = vals[mwp]
        if v:
            dam_num = v[0]
            dam_size = v[1]
            return dam_num, dam_size

    def calc_hit(self):
        hit_roll = min(
            99,
            int(self.translate(self.olvl, 1, 250, 40, 100)) +
            int(self.translate(self.diff.value, 0, 5, -5, 25)))
        return hit_roll
