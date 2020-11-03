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

    def func(self):
        from evennia.utils.evmenu import EvMenu

        ch = self.caller
        ch.msg(f"You are generating new character for {ch.name}")
        EvMenu(ch, "world.char_gen", startnode="pick_race", cmdset_mergetype='Replace', cmdset_priority=1, auto_quit=True)