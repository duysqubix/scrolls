"""
online editting of zones
restricted to wiz levels and up
"""
import evennia
from world.globals import BUILDER_LVL, DEFAULT_ZONE_STRUCT
from world.utils.utils import is_builder, is_online, is_pc, match_string
from evennia import CmdSet, Command, GLOBAL_SCRIPTS
from evennia.utils import wrap
from evennia.commands.default.help import CmdHelp
from .model import _EditMode

_ZEDIT_PROMPT = "(|gzedit|n)"


class ZEditMode(_EditMode):
    __cname__ = 'zone'
    __db__ = GLOBAL_SCRIPTS.zonedb
    __prompt__ = _ZEDIT_PROMPT
    __default_struct__ = DEFAULT_ZONE_STRUCT

    def save(self, override=False):
        if (self.orig_obj != self.obj) or override:
            # here assign zone_attributes to builders

            self.db.vnum[self.vnum] = self.obj
            self.caller.msg("zone saved.")

    def summarize(self):
        builders = wrap(", ".join(self.obj['builders']))
        min_, max_ = self.obj['level_range']
        lvl_range = f"Min: {min_} Max: {max_}"
        msg = f"""

********Zone Summary*******

VNUM: [{self.vnum}]      ZONE:[|m{self.obj['name']}|n]

builders    : 
|y{builders}|n

lifespan    : |y{self.obj['lifespan']}|n
level_range : |m{lvl_range}|n
reset_msg   : 
|c{self.obj['reset_msg']}|n
        """

        self.caller.msg(msg)


class ZEditCmdSet(CmdSet):
    key = "ZEditMode"

    mergetype = "Replace"

    def at_cmdset_creation(self):
        self.add(Exit())
        self.add(Look())
        self.add(CmdHelp())
        self.add(Set())


class ZEditCommand(Command):
    def at_post_cmd(self):
        self.caller.msg(prompt=_ZEDIT_PROMPT)


class Set(ZEditCommand):
    """
    Sets various data on currently editting zone.

    Usage:
        set [keyword] [args]

    """
    key = 'set'
    valid_zone_attributes = list(DEFAULT_ZONE_STRUCT.keys())

    def func(self):
        ch = self.caller
        args = self.args.strip().split()
        obj = ch.ndb._zedit.obj
        if not args:
            attrs = self.valid_zone_attributes.copy()
            keywords = "|n\n*|c".join(attrs)
            ch.msg(
                f'You must provide one of the valid keywords.\n*|c{keywords}')
            return

        keyword = args[0].lower()
        set_str = f"{keyword} set"
        if keyword in ('name', 'reset_msg'):
            if len(args) == 1:
                ch.msg("Must supply name for zone")
                return

            joiner = " " if keyword != 'name' else "_"
            obj[keyword] = f"{joiner}".join(args[1:]).strip()
            ch.msg(set_str)
            return
        elif match_string(keyword, 'builders'):
            if len(args) == 1:
                ch.msg("Supply builder names by spaces")
                return
            builders = args[1:]
            if 'clear' in builders:
                ch.msg("clearing all builders")
                obj['builders'].clear()
                return

            for builder in builders:

                builder = evennia.search_object(
                    builder, typeclass='typeclasses.characters.Character')
                if not builder or not is_pc(builder[0]):
                    ch.msg("no one like that exists")
                    continue

                builder = builder[0]
                if not is_builder(builder):
                    ch.msg(
                        f"{builder.name.capitalize()} is not at least lvl {BUILDER_LVL}"
                    )
                    return

                if builder.name not in obj['builders']:
                    obj['builders'].append(builder.name)

                    ch.msg(f"adding `{builder.name.capitalize()}` as builder")
                else:
                    obj['builders'].remove(builder.name)
                    ch.msg(
                        f"removing `{builder.name.capitalize()}` as builder")
            return

        else:
            ch.msg("That isn't a valid keyword")
            return


class Look(ZEditCommand):
    """
    view currently editing rooms main stats

    Usage:
        look|ls|l
    """

    key = "look"
    aliases = ['l', 'ls']

    def func(self):
        self.caller.ndb._zedit.summarize()


class Exit(ZEditCommand):
    """
    Exit redit

    Usage:
        exit
    """
    key = 'exit'

    def func(self):
        ch = self.caller
        ch.cmdset.remove('world.edit.zedit.ZEditCmdSet')
        ch.ndb._zedit.save()
        del ch.ndb._zedit