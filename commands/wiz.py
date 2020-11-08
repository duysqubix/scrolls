import evennia
from evennia.utils.evmenu import EvMenu
from commands.command import Command
from world.globals import BUILDER_LVL, WIZ_LVL

__all__ = ["CmdSpawn", "CmdCharacterGen"]


class CmdSpawn(Command):
    """
    spawn an instance of object or mob based on vnum

    Usage:
        spawn <obj/mob> <vnum>
    """

    key = "spawn"
    locks = f"attr_ge(level, {BUILDER_LVL}"

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
    locks = f"attr_ge(level, {WIZ_LVL}"
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

            if not evennia.utils.inherits_from(
                    char, 'typeclasses.characters.Character'):
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
