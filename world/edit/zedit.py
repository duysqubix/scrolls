"""
online editting of zones
restricted to wiz levels and up
"""
from typeclasses.rooms.rooms import get_room
import evennia
from evennia import TICKER_HANDLER as tickerhandler

from world.globals import BUILDER_LVL, DEFAULT_ZONE_STRUCT
from world.utils.utils import is_builder, is_online, is_pc, match_string
from evennia import CmdSet, Command, GLOBAL_SCRIPTS, create_script
from evennia.utils import wrap
from evennia.commands.default.help import CmdHelp
from world.utils.db import search_roomdb

from .model import _EditMode

_ZEDIT_PROMPT = "(|gzedit|n)"


def zone_reset(**kwargs):
    # get all rooms
    rooms = search_roomdb(zone=kwargs['name'], return_keys=True)
    if not rooms:
        return

    for vnum in rooms:
        room_obj = get_room(vnum)
        if not room_obj:
            continue
        room_obj.reset()
        room_obj.announce(kwargs['reset_msg'])


class ZEditMode(_EditMode):
    __cname__ = 'zone'
    __db__ = GLOBAL_SCRIPTS.zonedb
    __prompt__ = _ZEDIT_PROMPT
    __default_struct__ = DEFAULT_ZONE_STRUCT

    def save(self, override=False):
        if (self.orig_obj != self.obj) or override:
            try:
                reset_min = int(self.orig_obj['lifespan'])
                tickerhandler.remove(
                    reset_min * 60,
                    zone_reset,
                    idstring=f"zone_{self.orig_obj['name']}_reset")
                # self.caller.msg("removed ticker")
            except:
                pass

            self.db.vnum[self.vnum] = self.obj
            # update and/or create the RoomReset Script on all
            # rooms that exist within the saved zone.
            reset_min = int(self.obj['lifespan'])
            tickerhandler.add(reset_min * 60,
                              zone_reset,
                              f"zone_{self.obj['name']}_reset",
                              persistent=True,
                              **self.obj)
            # self.caller.msg("added ticker")
            self.caller.msg("zone saved.")

    def summarize(self):
        builders = wrap(", ".join(self.obj['builders']))
        min_, max_ = self.obj['level_range']
        lvl_range = f"Min: {min_} Max: {max_}"

        vnum_range = self.obj['vnums']
        vnums = f"|R{vnum_range[0]}|n to {vnum_range[1]}|R"
        msg = f"""

********Zone Summary*******

|GVNUM|n: [{self.vnum}]      |GZONE|n:[|m{self.obj['name']}|n]

|Gbuilders|n    : 
{builders}

|Glifespan|n    : |y{self.obj['lifespan']}|n
|Glevel_range|n : |m{lvl_range}|n
|Gvnums|n       : {vnums}
|Greset_msg|n   : 
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
        elif match_string(keyword, 'lifespan'):
            if not args:
                obj['lifespan'] = 10
            else:
                try:
                    ls = int(args[1])
                except ValueError:
                    ch.msg("Unable to parse lifespan into an integer")
                    return

                obj['lifespan'] = ls
            ch.msg(set_str.format(keyword='lifespan'))

        elif match_string(keyword, "vnums"):
            if not args:
                obj['vnums'] = [-1, -1]

            if len(args) != 3:
                ch.msg("provide a low and high vnum limit")
                return

            try:
                low = int(args[1])
                high = int(args[2])
            except ValueError:
                ch.msg("vnums are not valid numbers")
                return

            vnum_ranges = [(x, y['vnums'])
                           for x, y in ch.ndb._zedit.db.vnum.items()]

            for zone_vnum, range_ in vnum_ranges:
                new_range = set(range(low, high))
                cur_range = set(range(range_[0] - 1, range_[1] + 1))
                intersect = new_range & cur_range

                if len(intersect) > 0 and zone_vnum != ch.ndb._zedit.vnum:
                    ch.msg(
                        f"Invalid vnum range, vnums already taken, {range_[0], range_[1]}"
                    )
                    return
                obj['vnums'] = [low, high]
                ch.msg(set_str.format(keyword="vnums"))
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
        ch.ndb._zedit.save(override=True)
        del ch.ndb._zedit