from typeclasses.mobs.mob import VALID_MOB_APPLIES, VALID_MOB_FLAGS
from evennia import CmdSet, Command, EvEditor, GLOBAL_SCRIPTS
from evennia.commands.default.help import CmdHelp
from evennia.utils.utils import crop, list_to_string, wrap
from world.globals import DAM_TYPES, DEFAULT_MOB_STRUCT, Positions, Size
from world.edit.model import _EditMode

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
        self.caller.msg(list(self.obj.keys()))
        s = self.obj['stats']
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

Str: {s['str']:<3}  Wp : {s['wp']:<3}    HP: {s['hp']:<3}   dam_roll: {s['dam_roll']:<5}
End: {s['end']:<3}  Prc: {s['prc']:<3}    MP: {s['mp']:<3}   hit_roll: {s['hit_roll']:<5}
Agi: {s['agi']:<3}  Prs: {s['prs']:<3}    SP: {s['sp']:<3}   
Int: {s['int']:<3}  Lck: {s['lck']:<3}    AR: {s['ar']:<3}

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


class MEditCommand(Command):
    def at_post_cmd(self):
        self.caller.msg(prompt=_MEDIT_PROMPT)


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