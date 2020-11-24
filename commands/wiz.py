import json
import pathlib
from world.edit.zedit import ZEditMode
from world.edit.redit import REditMode
from typeclasses.objs.custom import CUSTOM_OBJS
from evennia.utils.utils import dedent, inherits_from, make_iter
from world.edit.oedit import OEditMode
from world.utils.utils import delete_contents, is_invis, match_string
from world.conditions import HolyLight, get_condition
from world.utils.act import Announce, act
from evennia import EvMenu, create_object, search_object
from commands.command import Command
from world.globals import BUILDER_LVL, GOD_LVL, WIZ_LVL, IMM_LVL
from evennia import GLOBAL_SCRIPTS
from evennia.utils import crop, list_to_string
from evennia.utils.ansi import raw as raw_ansi
from server.conf.settings import BOOK_JSON

__all__ = [
    "CmdSpawn", "CmdCharacterGen", "CmdWizInvis", "CmdOEdit", "CmdOList",
    "CmdLoad"
]


class CmdZone(Command):
    """
    Sets a particular zone on a player, must be a BUILDER level or up
    Cannot start editing without a zone set.
    
    Usage:
        zone set   <player> <zonename>
        zone clear <player>
        zone list
    """

    key = 'zone'
    locks = f"attr_ge(level.value, {WIZ_LVL})"

    def func(self):
        ch = self.caller
        args = self.args.strip().split()
        if len(args) == 1 and args[0] == 'list':
            # list zones here

            return

        if len(args) == 2:
            action, player = args

            player = search_object(
                player, typeclass='typeclasses.characters.Character')[0]
            if not player or not player.has_account:
                ch.msg("There is no one like that online")
                return

            if action in ('clear'):
                # clear the zone name on character
                player.attributes.remove('assigned_zone')
                ch.msg(
                    f"You cleared zone assignment to {player.name.capitalize()}"
                )
                player.msg(f"{ch.name.capitalize()} cleared zones from you.")
            else:
                ch.msg("That isn't a valid command")
            return

        elif len(args) == 3:
            action, player, zonename = args
            player = search_object(
                player, typeclass='typeclasses.characters.Character')[0]
            if not player or not player.has_account:
                ch.msg("There is no one like that online")
                return

            if action in ('set'):
                # set a valid zone to player
                zones = [
                    x['name'] for x in GLOBAL_SCRIPTS.zonedb.vnum.values()
                ]
                if zonename not in zones:
                    ch.msg("That is not a valid zone")
                    return
                player.attributes.add('assigned_zone', zonename)
                ch.msg(
                    f"You set zone {zonename} to {player.name.capitalize()}")
                player.msg(
                    f"{ch.name.capitalize()} assigned zone {zonename} to you.")
                return


class CmdLoad(Command):
    """
    Load an object/mob

    Usage:
        load <obj/mob> <vnum>
    """

    key = 'load'
    locks = f"attr_ge(level.value, {BUILDER_LVL})"

    def func(self):
        ch = self.caller
        args = self.args.strip().split()

        if not args:
            ch.msg(f"{self.__doc__}")
            return
        if len(args) == 1:
            ch.msg("must supply valid vnum number")
            return
        # <obj/mob> <vnum>
        obj_type, vnum = args
        if obj_type.lower() not in ('obj', 'mob'):
            ch.msg("must supply either `obj` or `mob`")
            return

        try:
            vnum = int(vnum)
        except ValueError:
            ch.msg("invalid vnum number")
            return

        # check to see if vnum exists
        if vnum not in GLOBAL_SCRIPTS.objdb.vnum.keys():
            ch.msg(f"that {obj_type}:{vnum} does not exist")
            return
        obj_bp = GLOBAL_SCRIPTS.objdb.vnum[vnum]
        # create instance of object and either put in room
        obj_type = CUSTOM_OBJS[obj_bp['type']]
        obj = create_object(obj_type, key=vnum)
        obj.move_to(ch.location)
        act_msg = "$n motions $s hands around and $e creates"\
            f" |G{obj.db.sdesc}|n"
        act(act_msg, False, False, ch, None, None, Announce.ToRoom)
        act(f"You create |G{obj.db.sdesc}|n", False, False, ch, None, None,
            Announce.ToChar)


class CmdOList(Command):
    """
    Lists all available objects set in objdb

    Usage:
        olist
        olist <type|name> <criteria>
    """
    key = "olist"
    locks = f"attr_ge(level.value, {BUILDER_LVL})"

    def func(self):
        ch = self.caller
        ch.msg(self.args)
        args = self.args.strip()
        objdb = dict(GLOBAL_SCRIPTS.objdb.db.vnum)
        min_ = min(GLOBAL_SCRIPTS.objdb.db.vnum.keys())
        max_ = max(GLOBAL_SCRIPTS.objdb.db.vnum.keys())

        if not args:
            table = self.styled_table("VNum",
                                      "Description",
                                      "Type",
                                      border='incols')

            for vnum in range(min_, max_ + 1):
                data = objdb[vnum]
                vnum = raw_ansi(f"[|G{vnum:<4}|n]")
                sdesc = crop(raw_ansi(data['sdesc']), width=50) or ''
                table.add_row(vnum, sdesc, f"{data['type']}")

            msg = str(table)
            ch.msg(msg)
            return

        args = args.split(' ')
        if len(args) < 2:
            ch.msg("Supply either type or name to search for")
            return
        table = self.styled_table("VNum",
                                  "Description",
                                  "Type",
                                  border='incols')
        type_ = args[0]
        if type_ not in ('type', 'name'):
            ch.msg("Please supply either (type or name) to searchby")
            return

        criteria = args[1]

        for vnum in range(min_, max_ + 1):
            # for vnum, data in GLOBAL_SCRIPTS.objdb.vnum.items():
            data = objdb[vnum]
            if type_ == 'type':
                if criteria == data['type']:
                    vnum = raw_ansi(f"[|G{vnum:<4}|n]")
                    sdesc = crop(raw_ansi(data['sdesc']), width=50) or ''
                    table.add_row(vnum, sdesc, f"{data['type']}")
                    continue
            if type_ == 'name':
                if criteria in data['key']:
                    vnum = raw_ansi(f"[|G{vnum:<4}|n]")
                    sdesc = crop(raw_ansi(data['sdesc']), width=50) or ''
                    table.add_row(vnum, sdesc, f"{data['type']}")
                    continue
        msg = str(table)
        ch.msg(msg)
        return


class CmdZList(Command):
    """
    Lists all available zones set in zoneb

    Usage:
        zlist
        zlist <name> <criteria>
    """
    key = "zlist"
    locks = f"attr_ge(level.value, {BUILDER_LVL})"

    def func(self):
        ch = self.caller
        ch.msg(self.args)
        args = self.args.strip()
        zonedb = dict(GLOBAL_SCRIPTS.zonedb.vnum)
        vnum_zonedb = zonedb.keys()
        min_ = min(vnum_zonedb)
        max_ = max(vnum_zonedb)

        legend = ["VNum", "Name", "Builders"]
        try:
            _ = zonedb[1]
        except KeyError:
            ch.msg("No zones are saved to database, try creating one first")
            return

        if not args:
            table = self.styled_table(*legend, border='incols')

            for vnum in range(min_, max_ + 1):
                data = zonedb[vnum]
                vnum = raw_ansi(f"[|G{vnum:<4}|n]")
                table.add_row(vnum, data['name'],
                              list_to_string(data['builders']))

            msg = str(table)
            ch.msg(msg)
            return

        args = args.split(' ')
        if len(args) < 2:
            ch.msg("Supply name to search for")
            return
        table = self.styled_table(*legend, border='incols')
        type_ = args[0]
        if type_ not in ('name'):
            ch.msg("Please supply name to search by")
            return

        criteria = args[1]
        for vnum in range(min_, max_ + 1):
            # for vnum, data in GLOBAL_SCRIPTS.objdb.vnum.items():
            data = zonedb[vnum]
            if type_ == 'name':
                if match_string(criteria, data['name'].split()):
                    vnum = raw_ansi(f"[|G{vnum:<4}|n]")
                    table.add_row(vnum, data['name'],
                                  list_to_string(data['builders']))
                    continue
        msg = str(table)
        ch.msg(msg)
        return


class CmdZEdit(Command):
    """
    Generic zone building command

    Usage:
        zedit <new|vnum>
    
    Opens the zone building menu. This allows to change the zone 
    details. To create a new zone with the next available vnum supply
    the `new` argument.
    """

    key = 'zedit'
    locks = f"attr_ge(level.value, {IMM_LVL})"

    def func(self):
        if not self.args.strip():
            self.msg("You must provide either a vnum or `new`")
            return

        zonedb = GLOBAL_SCRIPTS.zonedb
        ch = self.caller

        if 'new' in self.args.lower():
            if not zonedb.vnum.keys():
                vnum = 1
            else:
                vnum = max(zonedb.vnum.keys()) + 1
        else:
            vnum = self.args
            try:
                vnum = int(vnum)
            except ValueError:
                ch.msg("You must supply a valid vnum")
                return

        ch.ndb._zedit = ZEditMode(self, vnum)
        ch.cmdset.add("world.edit.zedit.ZEditCmdSet")
        ch.cmdset.all()[-1].add(CmdZList())
        ch.execute_cmd("look")


class CmdREdit(Command):
    """
    Generic room building command

    Usage:
        redit <new|vnum>
    
    Opens the room building menu. This allows to change the rooms 
    details. To create a new room with the next available vnum supply
    the `new` argument.
    """

    key = 'redit'
    locks = f"attr_ge(level.value, {BUILDER_LVL})"

    def func(self):
        if not self.args.strip():
            self.msg("You must provide either a vnum or `new`")
            return

        if not self.attributes.has('assigned_zone'):
            self.msg("You must be assigned a zone before you can edit rooms.")
            return

        roomdb = GLOBAL_SCRIPTS.roomdb
        ch = self.caller

        if 'new' in self.args.lower():
            if not roomdb.vnum.keys():
                vnum = 1
            else:
                vnum = max(roomdb.vnum.keys()) + 1
        else:
            vnum = self.args
            try:
                vnum = int(vnum)
            except ValueError:
                ch.msg("You must supply a valid vnum")
                return

        ch.ndb._redit = REditMode(self, vnum)
        ch.cmdset.add("world.edit.redit.REditCmdSet")
        ch.cmdset.all()[-1].add(CmdRList())
        ch.execute_cmd("look")


class CmdRList(Command):
    """
    Lists all available rooms set in objdb

    Usage:
        rlist
        rlist <zone||name> <criteria>
    """
    key = "rlist"
    locks = f"attr_ge(level.value, {BUILDER_LVL})"

    def func(self):
        ch = self.caller
        ch.msg(self.args)
        args = self.args.strip()
        roomdb = dict(GLOBAL_SCRIPTS.roomdb.vnum)
        vnum_roomdb = roomdb.keys()
        min_ = min(vnum_roomdb)
        max_ = max(vnum_roomdb)

        legend = ["VNum", "Name", "Exits", "Zone"]
        try:
            _ = roomdb[1]
        except KeyError:
            ch.msg("No rooms are saved to database, try creating one first")
            return

        if not args:
            table = self.styled_table(*legend, border='incols')

            for vnum in range(min_, max_ + 1):
                data = roomdb[vnum]
                exits = {k: v for k, v in data['exits'].items() if v > 0}
                vnum = raw_ansi(f"[|G{vnum:<4}|n]")
                sdesc = crop(raw_ansi(data['name']), width=50) or ''
                table.add_row(vnum, sdesc, f"{exits}", data['zone'])

            msg = str(table)
            ch.msg(msg)
            return

        args = args.split(' ')
        if len(args) < 2:
            ch.msg("Supply either type or name to search for")
            return
        table = self.styled_table(*legend, border='incols')
        type_ = args[0]
        if type_ not in ('zone', 'name'):
            ch.msg("Please supply either (type or name) to searchby")
            return

        criteria = args[1]
        for vnum in range(min_, max_ + 1):
            # for vnum, data in GLOBAL_SCRIPTS.objdb.vnum.items():
            data = roomdb[vnum]
            if type_ == 'zone':
                if match_string(criteria, make_iter(data['zone'])):
                    exits = {k: v for k, v in data['exits'].items() if v > 0}

                    vnum = raw_ansi(f"[|G{vnum:<4}|n]")
                    sdesc = crop(raw_ansi(data['name']), width=50) or ''
                    table.add_row(vnum, sdesc, f"{exits}", data['zone'])
                    continue

            if type_ == 'name':
                if match_string(criteria, data['name'].split()):
                    exits = {k: v for k, v in data['exits'].items() if v > 0}

                    vnum = raw_ansi(f"[|G{vnum:<4}|n]")
                    sdesc = crop(raw_ansi(data['name']), width=50) or ''
                    table.add_row(vnum, sdesc, f"{exits}", data['zone'])
                    continue
        msg = str(table)
        ch.msg(msg)
        return


class CmdOEdit(Command):
    """
    Generic building command.

    Syntax:
      oedit <vnum/name>

    Open a building menu to edit the specified object.  This menu allows to
    change the object's key and description.

    Examples:
      oedit new    # creates a new object with the next available vnum
      oedit 1231    #edit of object vnum:1231

    """

    key = "oedit"
    locks = f"attr_ge(level.value, {BUILDER_LVL})"

    def func(self):
        if not self.args.strip():
            self.msg("You must provide vnum to edit or `new`")
            return

        objdb = GLOBAL_SCRIPTS.objdb
        ch = self.caller

        if 'new' in self.args.lower():
            if not objdb.vnum.keys():
                vnum = 1
            else:
                vnum = max(objdb.vnum.keys()) + 1
        else:
            vnum = self.args
            try:
                vnum = int(vnum)
            except ValueError:
                ch.msg("you must supply a valid vnum")
                return

        ch.ndb._oedit = OEditMode(self, vnum)
        ch.cmdset.add('world.edit.oedit.OEditCmdSet')
        ch.execute_cmd("look")


class CmdPurge(Command):
    """
    Purge all contents in room that isn't character

    Usage:
        purge
    """

    key = 'purge'
    locks = f"attr_ge(level.value, {IMM_LVL})"

    def func(self):
        ch = self.caller

        delete_contents(ch.location)
        act("With an ear splitting bang, $n clears the room", False, False, ch,
            None, None, Announce.ToRoom)
        act("You clear the room", False, False, ch, None, None,
            Announce.ToChar)


class CmdHolyLight(Command):
    """
    Cast a holy light around you and be able to see everything
    
    Usage:
        holylight
    """
    key = 'holylight'
    aliases = ['holy']
    locks = f"attr_ge(level.value, {IMM_LVL})"

    def func(self):
        ch = self.caller

        holylight = get_condition('holy_light')
        if not ch.conditions.has(HolyLight):
            ch.conditions.add(holylight)
        else:
            ch.conditions.remove(holylight)


class CmdWizInvis(Command):
    """
    wizard level invisibility

    Usage:
        wizinvis
    """

    key = 'wizinvis'
    locks = f"attr_ge(level.value, {IMM_LVL})"

    def func(self):
        ch = self.caller

        invis = get_condition('invisible')
        if not is_invis(ch):
            ch.conditions.add(invis)
            act("You slowly vanish into thin air.", False, False, ch, None,
                None, Announce.ToChar)
            act("$n slowly vanishes into thin air.", False, False, ch, None,
                None, Announce.ToRoom)
        else:
            ch.conditions.remove(invis)
            act("You fade back to normal.", False, False, ch, None, None,
                Announce.ToChar)
            act("$n slowly fades back into normal", False, False, ch, False,
                None, Announce.ToRoom)


class CmdRestore(Command):
    """
    Fully restore an player/mob

    Usage:
        restore <obj>
    """
    key = "restore"
    locks = f"attr_ge(level.value, {IMM_LVL})"
    arg_regex = r"\s|$"

    def func(self):
        ch = self.caller
        if not self.args:
            act("You are restored", False, False, ch, None, None,
                Announce.ToRoom)
            act("You restore the room", False, False, ch, None, None,
                Announce.ToChar)
            ch.full_restore()
            return

        self.args = self.args.strip().split(' ')
        vict_obj = ch.location.search(self.args[0])
        if not vict_obj:
            ch.msg("You don't see anyone here by that name")
            return

        if vict_obj.is_pc or vict_obj.is_npc:
            vict_obj.full_restore()
            return


class CmdBookLoad(Command):
    """
    Creates/adds/overwrites internal database
    for books based on books.json
    """

    key = 'book_load'
    locks = f"attr_ge(level.value, {GOD_LVL}"
    arg_regex = r"\s|$"

    def func(self):
        ch = self.caller
        #TODO: find a better way to get book.json file
        from evennia import GLOBAL_SCRIPTS

        file = (pathlib.Path(__file__).parent.parent / "resources" / "books" /
                "books.json").absolute()
        with open(file) as b:
            books = json.load(b)

        # delete all books in db
        for k, v in dict(GLOBAL_SCRIPTS.objdb.db.vnum).items():
            if v['type'] == 'book':
                del GLOBAL_SCRIPTS.objdb.db.vnum[k]

        current_vnums = list(GLOBAL_SCRIPTS.objdb.db.vnum.keys())
        # find missing vnums
        a = list(range(1, current_vnums[-1] + 1))

        missing_vnums = list(set(current_vnums) ^ set(a))

        obj_info = {
            'edesc': "",
            'adesc': "",
            'type': 'book',
            'weight': 0,
            'cost': 0,
            'level': 1,
            'applies': [],
            'tags': []
        }
        book_idx = 0
        # fill in missing vnums first
        for vnum in missing_vnums:

            books[book_idx].update(obj_info)
            GLOBAL_SCRIPTS.objdb.db.vnum[vnum] = books[book_idx]
            book_idx += 1

        next_vnum = max(GLOBAL_SCRIPTS.objdb.db.vnum.keys()) + 1
        # create new ones
        ch.msg(str((len(books), book_idx, next_vnum)))
        for book in books[book_idx:]:
            ch.msg("adding book")
            book.update(obj_info)
            GLOBAL_SCRIPTS.objdb.db.vnum[next_vnum] = book
            next_vnum += 1

        ch.msg("loaded books")


class CmdCharacterGen(Command):
    """
    Wizard only command that takes you through the character generation process

    Usage:
        chargen <character>
    """

    key = "chargen"
    locks = f"attr_ge(level.value, {WIZ_LVL}"
    arg_regex = r"\s|$"

    def func(self):
        ch = self.caller
        if not self.args:
            char = ch
        else:
            self.args = self.args.strip().split(' ')

            char_name = self.args[0]
            char = evennia.search_object(char_name)
            if not char:
                ch.msg(f"There is no such character as {char_name}")
                return
            char = char[0]

            if not char.has_account:
                ch.msg("You cannot do a chargen with that object.")
                return

            if not char.is_connected:
                ch.msg(f"{char.name} is not online")
                return

        EvMenu(char,
               "world.chargen.gen",
               startnode="pick_race",
               cmdset_mergetype='Replace',
               cmdset_priority=1,
               auto_quit=True)
