from typeclasses.mobs.mob import VALID_MOB_APPLIES, VALID_MOB_FLAGS
from evennia import CmdSet, Command, EvEditor, GLOBAL_SCRIPTS
from evennia.commands.default.help import CmdHelp
from evennia.utils.utils import crop, list_to_string, wrap
from world.globals import DAM_TYPES, DEFAULT_MOB_STRUCT, Positions
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
----------------Stats---------------------
Level: {self.obj['level']}
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
                # list all available applies (conditions)
                table = self.styled_table("Available NPC Affects")
                affects = list_to_string(VALID_MOB_APPLIES)
                table.add_row(wrap(affects, width=50))
                ch.msg(table)
                return

        # elif keyword in ('weight', 'cost', 'level'):
        #     # set can't be < 0
        #     try:
        #         weight = int(args[1].strip())
        #     except:
        #         ch.msg(f"{keyword} not a valid integer")
        #         return

        #     if weight < 0:
        #         weight = 0
        #     obj[keyword] = weight
        #     ch.msg(f'{keyword} set.')
        #     return

        # elif keyword == 'applies':
        #     #args=    [0]     [1]    [2]    [3]  [4]
        #     # ex: set applies attrs [attr] [mod]
        #     # ex: set applies stats [stat] [mod]
        #     # ex: set applies conditions blinded x,y
        #     if len(args) > 1:
        #         if args[1] == 'clear':
        #             obj[keyword].clear()
        #             return
        #         if len(args) < 3:
        #             ch.msg("invalid entry, see |chelp oedit-menu-applies|n")
        #             return

        #         apply_type = args[1]
        #         if apply_type not in VALID_OBJ_APPLIES.keys():
        #             ch.msg("not a valid apply type")
        #             return

        #         if apply_type == 'attrs':
        #             attr = args[2]
        #             if attr not in VALID_OBJ_APPLIES['attrs']:
        #                 ch.msg("not a valid attribute to modify")
        #                 return
        #             try:
        #                 mod = int(args[3])
        #             except:
        #                 ch.msg("not a valid number for modifier")
        #                 return

        #             pair = (attr, mod)
        #             if pair in obj[keyword]:
        #                 obj[keyword].remove(pair)
        #                 return
        #             obj[keyword].append(pair)

        #         elif apply_type == 'stats':
        #             stat = args[2]
        #             if stat not in VALID_OBJ_APPLIES['stats']:
        #                 ch.msg("not a valid stat to modify")
        #                 return
        #             try:
        #                 mod = int(args[3])
        #             except:
        #                 ch.msg("not a valid number for modifier")
        #                 return

        #             pair = (stat, mod)
        #             if pair in obj[keyword]:
        #                 obj[keyword].remove(pair)
        #                 return
        #             obj[keyword].append(pair)

        #         elif apply_type == 'conditions':
        #             # ex: set applies conditions <condition> x y
        #             condition = args[2]
        #             if condition not in VALID_OBJ_APPLIES['conditions']:
        #                 ch.msg("not a valid condition")
        #                 return

        #             x, y = None, None
        #             if len(args) == 4:
        #                 # only x is given
        #                 try:
        #                     #TODO: sometimes x can be float depending on condition
        #                     x = int(args[3])
        #                 except:
        #                     ch.msg("X must be valid number")
        #                     return
        #             elif len(args) == 5:
        #                 # x and y is given
        #                 try:
        #                     x = int(args[3])
        #                     y = int(args[4])
        #                 except:
        #                     ch.msg("XY must be a valid number")
        #                     return

        #             pair = (condition, x, y)
        #             if pair in obj[keyword]:
        #                 obj[keyword].remove(pair)
        #                 return
        #             obj[keyword].append(pair)
        #         else:
        #             raise ValueError(
        #                 "bug encountered, you shouldn't have gotten here.")
        #     else:
        #         # show all applies
        #         applies = ""
        #         for apply_type, components in VALID_OBJ_APPLIES.items():
        #             applies += f"\n|c{apply_type}|n\n    "
        #             c = ", ".join(components)
        #             applies += c

        #         ch.msg(applies)
        #         return

        # elif keyword == 'tags':
        #     if len(args) > 1:
        #         tag = args[1].strip()

        #         if tag == 'clear':
        #             obj[keyword].clear()
        #             return
        #         if tag not in VALID_OBJ_TAGS:
        #             ch.msg("Not a valid tag")
        #             return
        #         if tag in obj[keyword]:
        #             obj[keyword].remove(tag)
        #             ch.msg(f"{tag} tag removed")
        #         else:
        #             obj[keyword].append(tag)
        #             ch.msg(f"{tag} tag applied")
        #         return
        #     else:
        #         # show all tags
        #         tags = ", ".join(VALID_OBJ_TAGS)
        #         msg = f"Available Tags:\n{tags}"
        #         ch.msg(msg)
        #         return


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