"""
online editting of room
"""

import re, copy
from evennia.utils.utils import wrap
from typeclasses.rooms.rooms import VALID_ROOM_FLAGS, VALID_ROOM_SECTORS, get_room
from world.utils.utils import clear_terminal, has_zone, match_name, match_string, mxp_string, next_available_rvnum, room_exists
from evennia import CmdSet, Command, EvEditor, search_object, create_object
from evennia.utils import crop, list_to_string
from typeclasses.rooms.custom import CUSTOM_ROOMS
from world.globals import DEFAULT_ROOM_STRUCT, OPPOSITE_DIRECTION, VALID_DIRECTIONS
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

    def init(self):
        assigned_zone = self.caller.attributes.get('assigned_zone')
        if not assigned_zone:
            raise Exception(
                "user should not be allowed in the first place with redit without a valid zone assigned"
            )

        if self.obj['zone'] == 'null':
            self.obj['zone'] = assigned_zone

        self.save(override=True)
        # create room object
        room = get_room(self.vnum)
        if not room:
            _ = create_object('typeclasses.rooms.rooms.Room', key=self.vnum)

    def save(self, override=False):
        if (self.orig_obj != self.obj) or override:
            # custom object checks here
            self.db.vnum[self.vnum] = self.obj

            #if room actually exists, update that too by calling its
            # appropriate method
            room = get_room(self.vnum)
            if room:
                room.at_object_creation()
            self.caller.msg("room saved.")

    def summarize(self):
        exit_summary = ""

        for ename, rvnum in self.obj['exits'].items():
            room = "" if get_room(rvnum) is None else get_room(rvnum).db.name
            exit_summary += f"    |y{ename.capitalize():<5}|n: {rvnum:<7} {room:<15}\n"

        edesc_msg = ""
        for key, edesc in self.obj['edesc'].items():
            edesc_msg += f"|c{key}|n:\n{crop(edesc)}\n"

        room_flags = list_to_string(self.obj['flags'])

        sector = self.obj['type']
        sector_symbol = VALID_ROOM_SECTORS[self.obj['type']].symbol

        status = "(|rCAN NOT EDIT|n)" if self.obj['zone'] != has_zone(
            self.caller) else ""
        msg = f"""
********Room Summary*******
        {status}
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
        self.add(Dig())
        self.add(Delete())
        self.add(New())


class REditCommand(Command):
    def at_post_cmd(self):
        self.caller.msg(prompt=_REDIT_PROMPT)


class New(REditCommand):
    """
    Creates a new room while in redit mode using next available vnum

    Usage:
        new
    """

    key = 'new'

    def func(self):
        ch = self.caller
        nextvnum = next_available_rvnum()
        new_room_info = copy.deepcopy(DEFAULT_ROOM_STRUCT)
        new_room_info['zone'] = has_zone(ch)

        ch.ndb._redit.__init__(ch, nextvnum)
        ch.ndb._redit.save(override=True)

        room = get_room(nextvnum)
        ch.move_to(room)
        ch.msg(f"Created new room vnum={nextvnum}")


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

        if has_zone(ch) != obj['zone']:
            ch.msg("You do not have permission to edit this zones room")
            return
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
            ch.msg("You can't set zone this way")
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
        elif match_string(keyword, 'exits'):
            if len(args) > 1:
                exit_name = args[1]
                if args[2] == 'clear':
                    exit_vnum = 'clear'
                else:
                    try:
                        exit_vnum = int(args[2])
                    except:
                        ch.msg("That is not a valid vnum")
                        return

                if exit_vnum == 'clear':
                    obj['exits'][exit_name] = -1
                else:
                    # check to see if exit_vnum is a valid vnum
                    if not room_exists(exit_vnum):
                        ch.msg("That room vnum does not exist")
                        return
                    obj['exits'][exit_name] = exit_vnum
                    ch.msg(set_str)

            else:
                ch.msg("Must provide a vnum to the exit")
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
        clear_terminal(self.caller)
        self.caller.ndb._redit.summarize()


class Exit(REditCommand):
    """
    Exit redit

    Usage:
        exit <True|False> <= weather to force a save or not
    """
    key = 'exit'

    def func(self):
        ch = self.caller
        ch.cmdset.remove('world.edit.redit.REditCmdSet')
        try:
            b = bool(eval(self.args.strip().capitalize()))
            ch.ndb._redit.save(override=b)
            del ch.ndb._redit
        except:
            ch.ndb._redit.save(override=False)
            del ch.ndb._redit


class Delete(Command):
    """
    Safely and cleanly deletes a room by vnum. Throws an error
    if the room does't exist in database. Only allows deletion of room
    if that room is in a zone that you are assigned too.

    Usage:
        delete <vnum>
    """

    key = 'delete'

    def func(self):
        ch = self.caller

        try:
            vnum = int(self.args.strip())
        except:
            ch.msg("Invalid vnum format")
            return

        room = get_room(vnum)
        if not room:
            # maybe it only exists in blueprints?
            try:
                del GLOBAL_SCRIPTS.roomdb.vnum[vnum]
                ch.msg(f"Successfully deleted room {vnum}")

            except KeyError:
                ch.msg("There is no such room")
            return
        else:

            if room.db.zone != has_zone(ch):
                ch.msg(
                    "You are not permitted to delete a room not in a zone assigned to you."
                )
                return

            # find all rooms that have exits that come to this room
            # delete those exits, since code only allows connecting rooms
            # within the same zone, this should be relatively low computationally
            # heavy.

            # search for all rooms within zone that has exit defined to this vnum
            for v, data in GLOBAL_SCRIPTS.roomdb.vnum.items():
                if data['zone'] != room.db.zone:
                    continue

                # room is in same zone
                # afgfected by it
                for direction, dest_vnum in data['exits'].items():
                    if dest_vnum == vnum:

                        # delete from roomdb
                        GLOBAL_SCRIPTS.roomdb.vnum[v]['exits'][direction] = -1
                        # delete exist from instance as well

                        ch.msg(f"Removed exit from room: {v}")

            # first safely remove blueprint of room
            del GLOBAL_SCRIPTS.roomdb.vnum[vnum]

            # move all contents in room to their 'home' location
            for obj in room.contents:
                obj.move_to(obj.home, quiet=True)
            room.delete()

            ch.msg(f"Successfully deleted room {vnum}")


class Dig(Command):
    """
    Dig a tunnel between two rooms, optional to create a exit from 
    original source

    Usage:
        dig <direction> remove 
        dig <bi/uni> <direction> [<vnum>]

    exs:
        dig bi north   # digs a bidirectional tunnel
        dig uni north # dig a a unidirectional room north.
        dig bi north 12 # digs  bidirectional tunnel to rvnum 12 if it exists
        dig bi north remove # removes both exits that linked the current room and target room
        dig uni north remove # removes current exit in the direction specific

    """

    key = 'dig'

    def func(self):
        ch = self.caller
        if not ch.attributes.has('assigned_zone'):
            self.msg("You must be assigned a zone before you can edit rooms.")
            return

        if not self.args:
            ch.msg(
                f"refer to {mxp_string('help dig', 'dig')} for more information"
            )
            return
        args = self.args.strip().split()
        if len(args) >= 2:
            vnum = None
            try:
                type_, direction, vnum = args
            except ValueError:
                type_, direction = args
            except:
                ch.msg(
                    f"incorrect format for dig.\nrefer to {mxp_string('help dig','dig')} for more information"
                )
                return

            if direction != 'remove':
                if type_ not in ('bi', 'uni'):
                    ch.msg("dig type must be either `bi` or `uni`")
                    return

                if not match_string(direction, VALID_DIRECTIONS):
                    ch.msg("must use a valid direction")
                    return

            if not vnum:
                cur_room = ch.ndb._redit.obj

                # first check if user is not wanting to remove an exit
                if direction == 'remove':
                    direction = type_
                    cur_room['exits'][direction] = -1
                    ch.ndb._redit.save(override=True)
                    ch.msg("Exit removed")
                else:
                    # dig in direction to new room and create exits from both ends

                    # get next available vnum, we are also guarenteed that room will
                    # not exist
                    nextvnum = next_available_rvnum()
                    new_room_info = copy.deepcopy(DEFAULT_ROOM_STRUCT)

                    # set exit of new room to the vnum of current room, using opposite
                    # direction from what was supplied (north->south, etc...)
                    if type_ == 'bi':
                        new_room_info['exits'][
                            OPPOSITE_DIRECTION[direction]] = ch.ndb._redit.vnum

                    # also set the zone for new room to cur_zone
                    new_room_info['zone'] = has_zone(ch)

                    #set exit of current room to the new room just created
                    cur_room['exits'][direction] = nextvnum

                    # actually create the object of new_room
                    # but just to be safe, let's make sure
                    room_exists = search_object(
                        str(nextvnum),
                        typeclass='typeclasses.rooms.rooms.Room')

                    # create and store blueprint of new room
                    ch.ndb._redit.db.vnum[nextvnum] = new_room_info

                    # create object
                    if not room_exists:  # if not exists
                        room = create_object('typeclasses.rooms.rooms.Room',
                                             key=nextvnum)
                    else:
                        room = room_exists[0]

                    # save current room in redit to update exits
                    ch.ndb._redit.save(override=True)

                    # change what redit sees, now we are editting new room
                    ch.ndb._redit.__init__(ch, nextvnum)
                    ch.ndb._redit.save(override=True)
                    # move to room
                    ch.move_to(room)

                return

            else:
                vnum = int(vnum)
                # first check to see if vnum of room exists
                target_room = search_object(
                    str(vnum), typeclass='typeclasses.rooms.rooms.Room')

                if not target_room:
                    # check to see if is in database
                    try:
                        target_room = GLOBAL_SCRIPTS.roomdb.vnum[vnum]
                    except KeyError:

                        ch.msg(
                            "room doesn't exist create it first and then rerun this command"
                        )
                        return
                    _ = create_object('typeclasses.rooms.rooms.Room', key=vnum)

                cur_room = ch.ndb._redit.obj
                target_room = target_room[0]
                if target_room.db.zone != cur_room['zone']:
                    ch.msg(
                        "You can't create an exit to a room that doesn't belong to this zone"
                    )
                    return

                if type_ == 'bi':
                    target_room['exits'][
                        OPPOSITE_DIRECTION[direction]] = ch.ndb._redit.vnum
                    ch.msg(
                        f"You created an exit in room {vnum} to your current location"
                    )

                cur_room['exits'][direction] = vnum
                ch.ndb._redit.save(override=True)

                ch.msg(f"Created exit to room {vnum}")
