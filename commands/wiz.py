from commands.command import Command
from world.globals import BUILDER_LVL

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