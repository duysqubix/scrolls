import json
import pathlib
from typeclasses.objs.custom import CUSTOM_OBJS
from evennia.utils.utils import dedent, inherits_from
import tabulate
from world.oedit import OEditMode
from world.utils.utils import is_invis
from world.conditions import DetectInvis, HolyLight, get_condition
from world.utils.act import Announce, act
import evennia
from evennia import EvMenu, create_object
from commands.command import Command
from world.globals import BUILDER_LVL, GOD_LVL, WIZ_LVL, IMM_LVL
from evennia import GLOBAL_SCRIPTS
from evennia.utils.ansi import ANSIParser
from evennia.utils import crop
from evennia.utils.ansi import raw as raw_ansi
from server.conf.settings import BOOK_JSON

__all__ = [
    "CmdSpawn", "CmdCharacterGen", "CmdWizInvis", "CmdOEdit", "CmdOList",
    "CmdLoad"
]


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
        if not args:
            table = self.styled_table("VNum",
                                      "Description",
                                      "Type",
                                      border='incols')
            for vnum, data in GLOBAL_SCRIPTS.objdb.vnum.items():
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

        for vnum, data in GLOBAL_SCRIPTS.objdb.vnum.items():
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
        ch.cmdset.add('world.oedit.OEditCmdSet')
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

        for obj in ch.location.contents:
            if inherits_from(obj, 'typeclasses.characters.Character'):
                continue
            obj.delete()

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

        # need to set basic obj settings:
        # key
        # sdesc
        # lsdesc
        for book in books:
            book.update({
                'edesc': "",
                'type': 'book',
                'weight': 0,
                'cost': 0,
                'level': 1,
                'applies': [],
                'extra': {},
                'tags': []
            })
            if book['key'] not in GLOBAL_SCRIPTS.objdb.db.vnum.keys():
                next_vnum = max(GLOBAL_SCRIPTS.objdb.db.vnum.keys()) + 1
                GLOBAL_SCRIPTS.objdb.db.vnum[next_vnum] = book
            else:
                # overwrite
                GLOBAL_SCRIPTS.objdb.db.vnum[]

        # ch.msg(data)


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
