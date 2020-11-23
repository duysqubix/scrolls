"""
online editting of room
"""

import re
from evennia.utils.utils import wrap
from typeclasses.rooms.rooms import VALID_ROOM_FLAGS, VALID_ROOM_SECTORS
from world.utils.utils import match_name, match_string
from evennia import CmdSet, Command, EvEditor, logger
from evennia.utils import crop, list_to_string
from typeclasses.rooms.custom import CUSTOM_ROOMS
from world.globals import DEFAULT_ROOM_STRUCT
from .model import _EditMode
from evennia import GLOBAL_SCRIPTS
from evennia.commands.default.help import CmdHelp
_REDIT_PROMPT = "(|rredit|n)"


class REditMode(_EditMode):
    __cname__ = 'room'
    __db__ = GLOBAL_SCRIPTS.roomdb
    __prompt__ = _REDIT_PROMPT
    __default_struct__ = DEFAULT_ROOM_STRUCT

    @property
    def custom_objs(self):
        return CUSTOM_ROOMS

    def save(self, override=False):
        if (self.orig_obj != self.obj) or override:
            # custom object checks here
            self.db.vnum[self.vnum] = self.obj
            self.caller.msg("room saved.")

    def summarize(self):
        exit_summary = ""

        for ename, rvnum in self.obj['exits'].items():
            exit_summary += f"    |y{ename.capitalize()}|n: {rvnum}\n"

        edesc_msg = ""
        for key, edesc in self.obj['edesc'].items():
            edesc_msg += f"|c{key}|n:\n{crop(edesc)}\n"

        room_flags = list_to_string(self.obj['flags'])

        sector = self.obj['type']
        sector_symbol = VALID_ROOM_SECTORS[self.obj['type']].symbol
        msg = f"""
********Room Summary*******

VNUM: [{self.vnum}]      ZONE:[|m{self.obj['zone']}|n]

name    : |y{self.obj['name']}|n
desc    : |y{self.obj['desc']}|n
flags   : 
|y{room_flags}|n

sector  : |m{sector}|n, [{sector_symbol}]
exits  : 
{exit_summary}

edesc   : 
{edesc_msg}
----------------Extras---------------------
"""
        for efield, evalue in self.obj['extra'].items():
            msg += f"{efield:<7}: {crop(evalue, width=50)}\n"
        self.caller.msg(msg)


class REditCmdSet(CmdSet):
    key = "REditMode"

    mergetype = "Replace"

    def at_cmdset_creation(self):
        self.add(Exit())
        self.add(Look())
        self.add(CmdHelp())
        self.add(Set())


class REditCommand(Command):
    def at_post_cmd(self):
        self.caller.msg(prompt=_REDIT_PROMPT)


class Set(REditCommand):
    """
    Sets various data on currently editting room.

    Usage:
        set [keyword] [args]

    """
    key = 'set'
    valid_room_attributes = list(DEFAULT_ROOM_STRUCT.keys())

    def func(self):
        ch = self.caller
        args = self.args.strip().split()
        obj = ch.ndb._redit.obj
        if not args:
            attrs = self.valid_room_attributes.copy()
            attrs[attrs.index('type')] = 'sector'
            keywords = "|n\n*|c".join(attrs)
            ch.msg(
                f'You must provide one of the valid keywords.\n*|c{keywords}')
            return

        keyword = args[0].lower()
        set_str = f"{keyword} set"
        if match_string(keyword, 'name'):
            if len(args) == 1:
                ch.msg("Must supply name for room")
                return
            obj['name'] = " ".join(args[1:]).strip()
            ch.msg(set_str)
            return

        elif match_string(keyword, 'desc'):
            if len(args) > 1:
                obj['desc'] = " ".join(args[1:]).strip()
                ch.msg(set_str)
            else:

                def save_func(_caller, buffer):
                    obj['desc'] = buffer
                    ch.msg(set_str)

                _ = EvEditor(ch,
                             loadfunc=(lambda _: obj['desc']),
                             savefunc=save_func)
            return
        elif match_string(keyword, 'sector'):
            if len(args) > 1:
                sector = args[1].strip()
                if sector not in VALID_ROOM_SECTORS.keys():
                    ch.msg("not a valid room sector")
                    return
                obj['type'] = sector
                return
            else:
                # show all sectors
                sectors = ", ".join(VALID_ROOM_SECTORS.keys())
                msg = f"Sectors:\n{wrap(sectors)}"
                ch.msg(msg)
                return
        elif match_string(keyword, 'edesc'):
            if len(args) > 1:
                ch.msg("set `edesc` without any arguments.")
            else:

                def save_func(_caller, buffer):
                    split = [
                        x.strip() for x in re.split("<(.*)>", buffer.strip())
                        if x
                    ]

                    if len(split) == 1:
                        # key not found
                        ch.msg("Keys must have <..> syntax.")
                        return

                    # uneven key/contents
                    if len(split) % 2 != 0:
                        # last elemet is key without content
                        split.append("n/a")

                    # create dictionary from keys/contents
                    edesc = dict([(k, v)
                                  for k, v in zip(split[::2], split[1::2])])

                    obj['edesc'] = edesc
                    ch.msg(set_str)

                if obj['edesc']:
                    edesc = ""
                    for key, contents in obj['edesc'].items():
                        edesc += f"<{key}>\n{contents}\n"
                else:
                    edesc = "<keyword> contents"
                _ = EvEditor(ch,
                             loadfunc=(lambda _: edesc),
                             savefunc=save_func)
        elif keyword == 'zone':
            if len(args) == 1:
                # list available zones here
                ch.msg("TODO: List all zones here")
                return
            else:
                ch.msg("TODO: search if valid zone ")
                return
        elif keyword == 'flags':
            if len(args) > 1:
                flag = args[1].strip()
                if flag == 'clear':
                    obj['flags'].clear()

                if flag not in VALID_ROOM_FLAGS:
                    ch.msg("Not a valid room flag")
                    return

                if flag in obj['flags']:
                    obj['flags'].remove(flag)
                    ch.msg(f"{flag} flag removed")
                else:
                    obj['flags'].append(flag)
                    ch.msg(f"{flag} flag applied")

            else:
                # show all foom flags
                flags = wrap(", ".join(VALID_ROOM_FLAGS))
                msg = f"Room Flags:\n{flags}"
                ch.msg(msg)
                return
        else:
            ch.msg("That isn't a valid keyword")
            return


class Look(REditCommand):
    """
    view currently editing rooms main stats

    Usage:
        look|ls|l
    """

    key = "look"
    aliases = ['l', 'ls']

    def func(self):
        self.caller.ndb._redit.summarize()


class Exit(REditCommand):
    """
    Exit redit

    Usage:
        exit
    """
    key = 'exit'

    def func(self):
        ch = self.caller
        ch.cmdset.remove('world.edit.redit.REditCmdSet')
        ch.ndb._redit.save()
        del ch.ndb._redit