import sys, time
import json
import pathlib
import traceback
from typeclasses.rooms.rooms import get_room

from evennia.utils.dbserialize import deserialize
from typeclasses.characters import Character
from typeclasses.mobs.mob import Mob

from evennia import EvMenu, create_object, search_object, GLOBAL_SCRIPTS, EvEditor
from evennia.commands.default.help import COMMAND_DEFAULT_CLASS
from evennia.commands.default.system import EvenniaPythonConsole
from evennia.utils import crop, list_to_string, inherits_from
from evennia.utils.ansi import raw as raw_ansi
from evennia.utils.utils import wrap

from world.edit.medit import MEditMode
from world.languages import VALID_LANGUAGES
from world.utils.db import search_mobdb, search_objdb, search_roomdb, search_zonedb
from commands.act_movement import CmdDown, CmdEast, CmdNorth, CmdSouth, CmdUp, CmdWest
from world.edit.zedit import ZEditMode
from world.edit.redit import REditMode
from typeclasses.objs.custom import CUSTOM_OBJS
from world.edit.oedit import OEditMode
from world.utils.utils import delete_contents, has_zone, is_invis, is_npc, is_pc, is_wiz, match_string
from world.conditions import HolyLight, get_condition
from world.utils.act import Announce, act
from commands.command import Command
from world.globals import BUILDER_LVL, GOD_LVL, WIZ_LVL, IMM_LVL


class CmdZReset(Command):
    """
    Manually resets rooms in current zone.

    Each reset `recreates` each room and loads
    objects and mobs based on 
    """

    key = 'zreset'

    def func(self):
        ch = self.caller

        zone = ch.location.db.zone
        # get rooms for current zone
        rooms = search_roomdb(zone=zone, return_keys=True)
        if not rooms:
            raise Exception('Current room does not have a zone assigned')

        for rvnum in rooms:
            room_obj = get_room(rvnum)
            if not room_obj:
                ch.msg(f"Room object doesn't exist, skipping {rvnum}")

            room_obj.reset()
        ch.msg(f"zone reset complete for {zone}")


class CmdForce(Command):
    """
    Force an object to do your bidding.
    Forces a pc/npc/obj to execute a command.
    Must be in same room.

    Usage:
        force <mob/pc> [cmd]

    Examples:
        force tavis say hello there, travelers.
        force puff emote picks his nose.
        force tavis east #forces tavis to move east
    """

    key = 'force'

    def func(self):
        ch = self.caller
        args = self.args.strip().split()

        if not args:
            ch.msg("force whom?")
            return

        if len(args) < 2:
            ch.msg("force whom to do what?")
            return

        target_name = args[0]
        cmd = " ".join(args[1:])

        target = None
        for obj in ch.location.contents:
            if is_npc(obj) and target_name in obj.db.key:
                target = obj
                break

            elif is_pc(obj) and target_name in obj.name:
                target = obj
                break
        if not target:
            ch.msg("You can't find anyone to do your bidding.")

        # force them
        ch.msg(f"You force {target_name} to `{cmd}`")
        act(f"$n forces you to {cmd}", False, False, ch, None, target,
            Announce.ToVict)
        target.execute_cmd(cmd)
        return


class CmdWizHelp(Command):
    """
    Shows available commands for wizards
    categorized by different wiz levels.

    Usage:
        wizhelp
    """

    key = 'wizhelp'

    def func(self):
        ch = self.caller

        cmdsets = ch.cmdset.all()

        table = self.styled_table("Staff Group", "Commands", border='cells')
        msg = ""
        start_level = GOD_LVL
        for cmdset in reversed(cmdsets):
            cmdset_name = f"{cmdset.key} ({start_level})"
            if cmdset.key == 'DefaultCharacter':
                continue

            commands = list_to_string([
                f"|c{x}|n"
                for x in sorted(cmdset.commands, key=lambda x: x.key)
            ])
            table.add_row(cmdset_name, wrap(commands, width=40))
            start_level -= 1
        ch.msg(str(table))


class CmdLanguageUpdate(Command):
    """
    Update language system.

    Usage:
        language_update [force]
    """

    key = 'language_update'

    def func(self):
        ch = self.caller
        args = self.args.strip()
        force = False
        if match_string('force', args):
            force = True

        for cls in VALID_LANGUAGES.values():
            lang = cls()
            ch.msg(f"Updating: {lang.__lang_name__}")
            lang.add(override=force)  # add langauge and overwrite


class CmdDBDump(Command):
    """
    Dumps zones/objects/room/mobs into json flat files.

    Useful for backups and clean wipes

    Usage:
        dbdump
    """

    key = 'dbdump'

    def func(self):
        ch = self.caller
        dump_ground = pathlib.Path(
            __file__).parent.parent / "resources" / "json"
        from evennia.utils.dbserialize import deserialize
        #zones
        zonedb = deserialize(GLOBAL_SCRIPTS.zonedb.vnum)
        objdb = deserialize(GLOBAL_SCRIPTS.objdb.vnum)
        roomdb = deserialize(GLOBAL_SCRIPTS.roomdb.vnum)
        mobdb = deserialize(GLOBAL_SCRIPTS.mobdb.vnum)
        books = []

        objs = {'zones': zonedb, 'rooms': roomdb, 'objs': objdb, 'mobs': mobdb}
        for fname, obj in sorted(objs.items()):
            if fname == 'objs':
                # remove books from dict
                for vnum, obj_value in tuple(obj.items()):
                    if obj_value['type'] == 'book':
                        book_details = dict()
                        for x in ('key', 'sdesc', 'ldesc', 'extra'):
                            book_details[x] = obj_value[x]
                        books.append(book_details.copy())
                        del obj[vnum]
            with open(dump_ground / f"{fname}.json", "w") as f:
                js = json.dumps(obj, indent=2)
                f.write(js)
                ch.msg(f"Wrote {fname} to file.")

        # store books now
        with open(dump_ground / "books.json", 'w') as f:
            js = json.dumps(books, indent=2)
            f.write(js)
            ch.msg("Wrote books to file")


class CmdGoto(Command):
    """
    Goto a particular room in based on the vnum.
    If the room blueprints exist, but not yet in the main database. 
    It will create the room based on the blueprints and move you there.

    Usage:
        goto <vnum>

    """

    key = 'goto'

    def func(self):
        ch = self.caller

        def poof(location):
            act("With a thunderous clap, $n leaves the room.", False, False,
                ch, None, None, Announce.ToRoom)
            ch.move_to(location)
            act("With a thunderous clap, $n enters the room.", False, False,
                ch, None, None, Announce.ToRoom)
            ch.execute_cmd('look')

        if not self.args:
            ch.msg("supply a rvnum or name of a player to go to")
            return

        # try to find person first
        target_name = self.args.strip()

        try:
            vnum = int(target_name)
        except:

            pc_target = search_object(target_name.lower(), typeclass=Character)
            npc_target_key = search_mobdb(key=target_name, return_keys=True)

            if not npc_target_key:
                npc_target = None
            else:
                npc_target = search_object(str(npc_target_key[0]),
                                           typeclass=Mob)

            if not pc_target and not npc_target:
                ch.msg("There is no one like that.")
                return

            # pc takes precedense over npc
            if pc_target:
                target = pc_target[0]
                if not target.has_account:
                    ch.msg("They are not online")
                    return
                poof(target.location)
                return

            if npc_target:
                target = npc_target[0]
                poof(target.location)
                return
            return

        # handle special case of void here
        if vnum == 1:
            void = search_object('#2')[0]
            poof(void)
            return

        # try to find vnum in database
        room = search_object(str(vnum),
                             typeclass='typeclasses.rooms.rooms.Room')
        roomdb = GLOBAL_SCRIPTS.roomdb

        if not room:
            # make sure a blueprint of room exists
            try:
                _ = roomdb.vnum[vnum]
            except KeyError:
                ch.msg("That room does not exist")
                return
            room = create_object('typeclasses.rooms.rooms.Room', key=vnum)
            poof(room)
        else:
            poof(room[0])


class CmdZoneSet(Command):
    """
    Sets a particular zone on a player, must be a BUILDER level or up
    Cannot start editing without a zone set.
    
    Usage:
        zone: shows current assigned zone if any
        zone set <player> <zonename>

    """

    key = 'zone'

    def func(self):
        ch = self.caller
        args = self.args.strip().split()
        if not args:
            zone = ch.db.assigned_zone
            zone = "none" if zone is None else zone
            zonemsg = f"You are assigned zone: |m{zone.replace('_', ' ')}|n"
            ch.msg(zonemsg)
            return

        action, player, zonename = args
        player = search_object(player,
                               typeclass='typeclasses.characters.Character')[0]
        if not player or not player.has_account:
            ch.msg("There is no one like that online")
            return

        if action in ('set'):
            if not is_wiz(ch):
                ch.msg("You are not permitted to do that.")
                return

            if zonename == 'clear':
                player.attributes.remove('assigned_zone')
                ch.msg(f"Zone cleared for {player.name.capitalize()}")
                return
            # set a valid zone to player
            zones = [x['name'] for x in GLOBAL_SCRIPTS.zonedb.vnum.values()]
            if zonename not in zones:
                ch.msg("That is not a valid zone")
                return
            if player.attributes.has(
                    'assigned_zone') and player.attributes.get(
                        'assigned_zone') == zonename:
                player.attributes.remove('assigned_zone')
                ch.msg(
                    f"You unassigned zone {zonename} to {player.name.capitalize()}"
                )
                player.msg(
                    f"{ch.name.capitalize()} unassigned zone {zonename} from you."
                )
            else:
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

        if obj_type == 'obj':
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

        elif obj_type == 'mob':
            if vnum not in GLOBAL_SCRIPTS.mobdb.vnum.keys():
                ch.msg(f"mob: {vnum} does not exist")
                return
            mob_bp = GLOBAL_SCRIPTS.mobdb.vnum[vnum]
            mob = create_object(Mob, key=vnum)
            mob.move_to(ch.location)
            act_msg = "$n motions $s hands around and $e creates"\
                f" |G{mob.db.sdesc}|n"
            act(act_msg, False, False, ch, None, None, Announce.ToRoom)
            act(f"You create |G{mob.db.sdesc}|n", False, False, ch, None, None,
                Announce.ToChar)
            ch.msg(f"You creating a mob: {vnum}")


class CmdOList(Command):
    """
    Lists all available objects set in objdb

    Usage:
        olist
        olist <type|name> <criteria>
        olist type criteria <extra_field> <extra_criteria>

        ex:
        olist                 # lists all objects in database
        olist type book       # lists all objects of type book
        olist type equipment  # list all objects of type equipment
        olist name fire       # list all objects named `fire`
        olist type book category fiction # list all books of fiction category
    """
    key = "olist"

    def func(self):
        ch = self.caller

        def show_table(dictionary):
            table = self.styled_table("VNum",
                                      "Description",
                                      "Type",
                                      border='incols')
            for vnum, data in sorted(dictionary.items()):
                vnum = raw_ansi(f"[|G{vnum:<4}|n]")
                desc = crop(raw_ansi(data['sdesc']), width=50) or ''
                type = data['type']
                table.add_row(vnum, desc, type)

            ch.msg(table)

        args = self.args.strip()
        objdb = deserialize(GLOBAL_SCRIPTS.objdb.vnum)

        if not objdb:
            ch.msg("There are no objects within the game")
            return

        if not args:
            objs = search_objdb('all')
            show_table(objs)
            return

        args = args.split(' ')
        if len(args) < 2:
            ch.msg("Supply either type or name to search for")
            return
        type_ = args[0]
        if type_ not in ('type', 'name'):
            ch.msg("Please supply either (type or name) to searchby")
            return

        if type_ == 'name':
            type_ = 'key'
        criteria = args[1]

        try:
            extra_field, extra_criteria = args[2], args[3]
            objs = search_objdb(**{type_: criteria},
                                extra=f"{extra_field} {extra_criteria}")

        except IndexError:
            objs = search_objdb(**{type_: criteria})
        show_table(objs)
        return


class CmdMList(Command):
    """
    Lists all available mobs set in mobdb

    Usage:
        mlist
        mlist name <name>
        mlist <criteria>
        mlist <criteria> [condition] <criteria> ...

        Valid conditions:
            && - logical and
            || - logical or
            ! -  logical not

        
        Conditions are evaluated LHF style.
        For example
        mlist key puff || key dragon && position standing ! attack bite

        will get monster that have either 'puff' or 'dragon' in 
        their key and only if they are default standing, but does
        contain the attack type of bite


        ex:
            #all mobs in db (defaults to zone only if editing a zone)
            mlist       

            # all mobs with name puff
            mlist name puff    

            #all mobs that have sneak,hidden added as default
            mlist applies sneak,hidden      

            
            # mobs with nosummon,aggr flags AND sneak,hidden in applies
            mlist flags nosummon,aggr && applies sneak,hidden


            mlist position standing && attack hit || applies sneak,hidden ! flags nosummon


    """
    key = "mlist"

    def func(self):
        ch = self.caller
        args = self.args.strip()
        mobdb = dict(GLOBAL_SCRIPTS.mobdb.vnum)

        if not mobdb:
            ch.msg("There are no mobs within the game")
            return

        def show_table(dictionary):
            table = self.styled_table("VNum",
                                      "Description",
                                      "Level",
                                      border='incols')
            for vnum, data in sorted(dictionary.items()):
                vnum = raw_ansi(f"[|G{vnum:<4}|n]")
                sdesc = crop(raw_ansi(data['sdesc']), width=50) or ''
                table.add_row(vnum, sdesc, data['level'])

            ch.msg(table)

        if not args:
            mobs = search_mobdb('all')
            show_table(mobs)
            return

        args = raw_ansi(args).split(' ')
        if args[0] == 'name' and len(args) == 2:
            mobs = search_mobdb(key=args[1])
            show_table(mobs)
            return
        else:
            if len(args) < 2:
                ch.msg("Must supply a field:value for each criteria")
                return
            if len(args) == 2:
                # process simple here
                field, value = args
                criteria = {field: value}
                mobs = search_mobdb(**criteria)
                show_table(mobs)
                return


class CmdZList(Command):
    """
    Lists all available zones set in zoneb

    Usage:
        zlist
        zlist <name> <criteria>
    """
    key = "zlist"

    def func(self):
        ch = self.caller

        def show_table(dictionary):
            table = self.styled_table("VNum",
                                      "Name",
                                      "Builders",
                                      border='incols')
            for vnum, data in sorted(dictionary.items()):
                vnum = raw_ansi(f"[|G{vnum:<4}|n]")
                table.add_row(vnum, data['name'],
                              list_to_string(data['builders']))

            ch.msg(table)

        args = self.args.strip()
        search_criteria = "all" if not args else args.strip()
        if not args:
            zones = search_zonedb('all')

            if not zones:
                ch.msg("No zones found.")
                return
            show_table(zones)
            return

        args = args.split(' ')
        if len(args) < 2:
            ch.msg("Supply name to search for")
            return
        type_, criteria = args

        zones = search_zonedb(**{type_: criteria})
        if not zones:
            ch.msg("No zones found matching the criteria")
            return

        show_table(zones)

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

    def func(self):
        ch = self.caller

        if not ch.attributes.has('assigned_zone'):
            self.msg("You must be assigned a zone before you can edit rooms.")
            return

        if not self.args.strip():
            # see if you ca edit the current room you are in.
            cur_room = ch.location

            room_zone = cur_room.db.zone
            if has_zone(ch) == room_zone:
                vnum = int(cur_room.key)
            else:
                self.msg("You don't have permission to edit this zones room.")
                return
        else:

            roomdb = GLOBAL_SCRIPTS.roomdb

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

        ch.ndb._redit = REditMode(ch, vnum)
        ch.cmdset.add("world.edit.redit.REditCmdSet")
        ch.cmdset.all()[-1].add([
            CmdRList(),
            CmdZoneSet(),
            CmdNorth(),
            CmdSouth(),
            CmdEast(),
            CmdWest(),
            CmdUp(),
            CmdDown()
        ])

        ch.execute_cmd("look")


class CmdRList(Command):
    """
    Lists all available rooms set in objdb. If you are assigned a zone,
    rlist will by default only show rooms in your zone.

    Usage:
        rlist
        rlist <zone||name> <parameter>

    Example

        rlist # returns all rooms, if assigned to zone, will return rooms only in current zone

        rlist zone myzone # returns room based in zone
        rlist name cellar # returns all rooms that matches cellar in room name
    """
    key = "rlist"

    def func(self):
        ch = self.caller

        def show_table(dictionary):
            table = self.styled_table("VNum",
                                      "Name",
                                      "Exits",
                                      "Zone",
                                      border='incols')
            for vnum, data in sorted(dictionary.items()):
                vnum = raw_ansi(f"[|G{vnum:<4}|n]")
                name = data['name']
                zone = data['zone']
                exits = [
                    f"{dir[0].capitalize()}[{num}]"
                    for dir, num in data['exits'].items() if num > 0
                ]
                table.add_row(vnum, name, list_to_string(exits), zone)

            ch.msg(table)

        args = self.args.strip()
        roomdb = dict(GLOBAL_SCRIPTS.roomdb.vnum)
        if not roomdb:
            ch.msg("There are no rooms within the game")
            return

        try:
            _ = roomdb[1]
        except KeyError:
            ch.msg("No rooms are saved to database, try creating one first")
            return

        if not args:
            ch_zone = has_zone(ch)

            if ch_zone:
                rooms = search_roomdb(zone=ch_zone)
            else:
                rooms = search_roomdb('all')
            show_table(rooms)

            return

        args = args.split(' ')
        if len(args) < 2:
            ch.msg("Supply either type or name to search for")
            return
        type_ = args[0]
        if type_ not in ('zone', 'name'):
            ch.msg("Please supply either (type or name) to searchby")
            return

        criteria = args[1]
        rooms = None
        if type_ == 'zone':
            rooms = search_roomdb(zone=criteria)
        elif type_ == 'name':
            rooms = search_roomdb(name=criteria)

        if not rooms:
            ch.msg("No such rooms were found")
            return

        show_table(rooms)
        return


class CmdOEdit(Command):
    """
    Generic building command.

    Syntax:
      oedit <vnum>
      oedit new

    Open a building menu to edit the specified object.  This menu allows to
    change the object's key and description.

    Examples:
      oedit new    # creates a new object with the next available vnum
      oedit 1231    #edit of object vnum:1231

    """

    key = "oedit"

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


class CmdMEdit(Command):
    """
    Generic building command for monsters.

    Syntax:
      medit <vnum>
      medit new

    Open a building menu to edit the specified monster.  

    Examples:
      medit new    # creates a new mob with the next available vnum
      medit 1231    #edit of mob vnum:1231

    """

    key = "medit"

    def func(self):
        ch = self.caller

        if not ch.attributes.has('assigned_zone'):
            self.msg("You must be assigned a zone before you can edit mobs.")
            return

        if not self.args.strip():
            self.msg("You must provide vnum to edit or `new`")
            return

        mobdb = GLOBAL_SCRIPTS.mobdb

        if 'new' in self.args.lower():
            if not mobdb.vnum.keys():
                vnum = 1
            else:
                vnum = max(mobdb.vnum.keys()) + 1
        else:
            vnum = self.args
            try:
                vnum = int(vnum)
            except ValueError:
                ch.msg("you must supply a valid vnum")
                return
            mob = search_mobdb(vnum)
            if mob:
                # check if you can edit this mob (has to be in same zone)
                if mob[vnum]['zone'] != has_zone(ch):
                    ch.msg("You don't have permissions to edit this mob. ")
                    return

        ch.ndb._medit = MEditMode(ch, vnum)
        ch.cmdset.add('world.edit.medit.MEditCmdSet')
        ch.execute_cmd("look")


class CmdPurge(Command):
    """
    Purge all contents in room that isn't character

    Usage:
        purge
    """

    key = 'purge'

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


class CmdDBLoad(Command):
    """
    Restore blueprints for mobs, objs, zones, and room
    using this command. It reads the associated json files found in
    |cresources|n folder and updates the associated blueprint databases

    Usage:
        dbload all


    """

    key = 'dbload'

    def func(self):
        ch = self.caller

        dumping_ground = pathlib.Path(
            __file__).parent.parent / "resources" / "json"

        def load_db(name):
            dbname = name + 'db'
            GLOBAL_SCRIPTS.get(dbname).vnum.clear()
            with open(dumping_ground / f"{name}s.json", "r") as f:
                data = json.load(f)
                for vnum, data in data.items():
                    GLOBAL_SCRIPTS.get(dbname).vnum[int(vnum)] = data
            ch.msg(f"loaded {name}")

        if not self.args:
            names = [f"|c{x.name[:-2]}|n"
                     for x in GLOBAL_SCRIPTS.all()] + ["|cbook|n"]
            ch.msg(f"Valid dbnames:\n|gall|n or\n{list_to_string(names)}")
            return

        args = self.args.strip()

        if args == 'all':
            for db in ('mob', 'room', 'zone', 'obj', 'trig', 'book'):
                if db == 'book':
                    ch.execute_cmd('book_load')
                    continue
                load_db(db)
            return
        if args == "book":
            ch.execute_cmd('book_load')
            return

        if args + 'db' not in [x.name for x in GLOBAL_SCRIPTS.all()]:
            ch.msg("That is not a valid dbname")
            return

        load_db(args)


class CmdBookLoad(Command):
    """
    Creates/adds/overwrites internal database
    for books based on books.json
    """

    key = 'book_load'
    arg_regex = r"\s|$"

    def func(self):
        ch = self.caller

        file = pathlib.Path(
            __file__).parent.parent / "resources" / "json" / "books.json"
        with open(file) as b:
            books = json.load(b)
        # delete all books in db
        for k, v in dict(GLOBAL_SCRIPTS.objdb.vnum).items():
            if v['type'] == 'book':
                del GLOBAL_SCRIPTS.objdb.vnum[k]

        current_vnums = list(GLOBAL_SCRIPTS.objdb.vnum.keys())
        book_idx = 0
        obj_info = {
            'edesc': "",
            'adesc': "",
            'type': 'book',
            'weight': 1,
            'cost': 0,
            'level': 1,
            'applies': [],
            'tags': []
        }

        next_vnum = 1
        if current_vnums:
            # find missing vnums
            a = list(range(1, current_vnums[-1] + 1))

            missing_vnums = list(set(current_vnums) ^ set(a))

            # fill in missing vnums first
            for vnum in missing_vnums:

                books[book_idx].update(obj_info)
                GLOBAL_SCRIPTS.objdb.vnum[vnum] = books[book_idx]
                book_idx += 1

            next_vnum = max(GLOBAL_SCRIPTS.objdb.vnum.keys()) + 1
        # create new ones
        # ch.msg(str((len(books), book_idx, next_vnum)))
        for book in books[book_idx:]:
            # ch.msg("adding book")
            book.update(obj_info)
            GLOBAL_SCRIPTS.objdb.vnum[next_vnum] = book
            next_vnum += 1

        ch.msg("loaded books")


class CmdCharacterGen(Command):
    """
    Wizard only command that takes you through the character generation process

    Usage:
        chargen <character>
    """

    key = "chargen"
    arg_regex = r"\s|$"

    def func(self):
        ch = self.caller
        if not self.args:
            char = ch
        else:
            self.args = self.args.strip().split(' ')

            char_name = self.args[0]
            char = search_object(char_name)
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


############################### IN-GAME PYTHON COMMAND ################################3
# Can't easily override some default actions on this without bringing some code over from base of evennia


class CmdPy(COMMAND_DEFAULT_CLASS):
    """
    execute a snippet of python code
    Usage:
      py [cmd]
      py/edit
      py/time <cmd>
      py/clientraw <cmd>
      py/noecho
    Switches:
      time - output an approximate execution time for <cmd>
      edit - open a code editor for multi-line code experimentation
      clientraw - turn off all client-specific escaping. Note that this may
        lead to different output depending on prototocol (such as angular brackets
        being parsed as HTML in the webclient but not in telnet clients)
      noecho - in Python console mode, turn off the input echo (e.g. if your client
        does this for you already)
    Without argument, open a Python console in-game. This is a full console,
    accepting multi-line Python code for testing and debugging. Type `exit()` to
    return to the game. If Evennia is reloaded, the console will be closed.
    Enter a line of instruction after the 'py' command to execute it
    immediately.  Separate multiple commands by ';' or open the code editor
    using the /edit switch (all lines added in editor will be executed
    immediately when closing or using the execute command in the editor).
    A few variables are made available for convenience in order to offer access
    to the system (you can import more at execution time).
    Available variables in py environment:
      self, me                   : caller
      here                       : caller.location
      evennia                    : the evennia API
      inherits_from(obj, parent) : check object inheritance
    You can explore The evennia API from inside the game by calling
    the `__doc__` property on entities:
        py evennia.__doc__
        py evennia.managers.__doc__
    |rNote: In the wrong hands this command is a severe security risk.  It
    should only be accessible by trusted server admins/superusers.|n
    """

    key = "py"
    aliases = ["!"]
    switch_options = ("time", "edit", "clientraw", "noecho")
    help_category = "System"

    def func(self):
        """hook function"""

        caller = self.caller
        pycode = self.args

        noecho = "noecho" in self.switches

        if "edit" in self.switches:
            caller.db._py_measure_time = "time" in self.switches
            caller.db._py_clientraw = "clientraw" in self.switches
            EvEditor(
                self.caller,
                loadfunc=_py_load,
                savefunc=_py_code,
                quitfunc=_py_quit,
                key="Python exec: :w  or :!",
                persistent=True,
                codefunc=_py_code,
            )
            return

        if not pycode:
            # Run in interactive mode
            console = EvenniaPythonConsole(self.caller)
            banner = ("|gEvennia Interactive Python mode{echomode}\n"
                      "Python {version} on {platform}".format(
                          echomode=" (no echoing of prompts)"
                          if noecho else "",
                          version=sys.version,
                          platform=sys.platform,
                      ))
            self.msg(banner)
            line = ""
            main_prompt = "|x[py mode - quit() to exit]|n"
            prompt = main_prompt
            while line.lower() not in ("exit", "exit()"):
                try:
                    line = yield (prompt)
                    if noecho:
                        prompt = "..." if console.push(line) else main_prompt
                    else:
                        prompt = line if console.push(
                            line) else f"{line}\n{main_prompt}"
                except SystemExit:
                    break
            self.msg("|gClosing the Python console.|n")
            return

        _run_code_snippet(
            caller,
            self.args,
            measure_time="time" in self.switches,
            client_raw="clientraw" in self.switches,
        )


def _evennia_local_vars(caller):
    """Return Evennia local variables usable in the py command as a dictionary."""
    import evennia

    return {
        "self": caller,
        "me": caller,
        "here": getattr(caller, "location", None),
        "evennia": evennia,
        "ev": evennia,
        "inherits_from": inherits_from,
        "search_objdb": search_objdb,
        "search_mobdb": search_mobdb,
        "search_zonedb": search_zonedb,
        "search_roomdb": search_roomdb
    }


def _run_code_snippet(caller,
                      pycode,
                      mode="eval",
                      measure_time=False,
                      client_raw=False,
                      show_input=True):
    """
    Run code and try to display information to the caller.
    Args:
        caller (Object): The caller.
        pycode (str): The Python code to run.
        measure_time (bool, optional): Should we measure the time of execution?
        client_raw (bool, optional): Should we turn off all client-specific escaping?
        show_input (bookl, optional): Should we display the input?
    """
    # Try to retrieve the session
    session = caller
    sessions = caller.sessions.all()

    available_vars = _evennia_local_vars(caller)

    if show_input:
        for session in sessions:
            try:
                caller.msg(">>> %s" % pycode,
                           session=session,
                           options={"raw": True})
            except TypeError:
                caller.msg(">>> %s" % pycode, options={"raw": True})
    # reroute standard output to game client console
    old_stdout = sys.stdout
    old_stderr = sys.stderr

    try:

        class FakeStd:
            def __init__(self, caller):
                self.caller = caller

            def write(self, string):
                self.caller.msg(string.rsplit("\n", 1)[0])

        fake_std = FakeStd(caller)
        sys.stdout = fake_std
        sys.stderr = fake_std

        try:
            pycode_compiled = compile(pycode, "", mode)
        except Exception:
            mode = "exec"
            pycode_compiled = compile(pycode, "", mode)

        duration = ""
        if measure_time:
            t0 = time.time()
            ret = eval(pycode_compiled, {}, available_vars)
            t1 = time.time()
            duration = " (runtime ~ %.4f ms)" % ((t1 - t0) * 1000)
            caller.msg(duration)
        else:
            ret = eval(pycode_compiled, {}, available_vars)

    except Exception:
        errlist = traceback.format_exc().split("\n")
        if len(errlist) > 4:
            errlist = errlist[4:]
        ret = "\n".join("%s" % line for line in errlist if line)
    finally:
        # return to old stdout
        sys.stdout = old_stdout
        sys.stderr = old_stderr

    if ret is None:
        return
    elif isinstance(ret, tuple):
        # we must convert here to allow msg to pass it (a tuple is confused
        # with a outputfunc structure)
        ret = str(ret)

    for session in sessions:
        try:
            caller.msg(ret,
                       session=session,
                       options={
                           "raw": True,
                           "client_raw": client_raw
                       })
        except TypeError:
            caller.msg(ret, options={"raw": True, "client_raw": client_raw})


#########################################################################################
