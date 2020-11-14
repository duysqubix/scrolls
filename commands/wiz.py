from world.utils.utils import is_invis
from world.conditions import get_condition
from world.utils.act import Announce, act
import evennia
from evennia.utils.evmenu import EvMenu
from commands.command import Command
from world.globals import BUILDER_LVL, WIZ_LVL, IMM_LVL
from evennia import GLOBAL_SCRIPTS
__all__ = ["CmdSpawn", "CmdCharacterGen", "CmdWizInvis", "CmdOEdit"]


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

        EvMenu(ch,
               "world.edit_menus.oedit",
               startnode='main_menu',
               cmdset_mergetype='Replace',
               cmdset_priority=1,
               auto_quit=True,
               auto_help=True,
               debug=True,
               vnum=vnum)


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
            act()
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


class CmdSpawn(Command):
    """
    spawn an instance of object or mob based on vnum

    Usage:
        spawn <obj/mob> <vnum>
    """

    key = "spawn"
    locks = f"attr_ge(level.value, {BUILDER_LVL}"

    def func(self):
        ch = self.caller
        ch.msg(f"spawning {self.args} for you")


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
