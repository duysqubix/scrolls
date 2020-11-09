from typeclasses.characters import Character
from evennia import CmdSet


class NpcBaseCmdSet(CmdSet):
    """
    The base cmdset for all npcs
    """

    key = 'DefaultNpc'

    def at_cmdset_creation(self):
        super().at_cmdset_creation()


class Npc(Character):
    @property
    def is_pc(self):
        return False

    def basetype_setup(self):
        super().basetype_setup()
        self.locks.add(";".join(["get:false()", "call:false()"]))

        # add the default cmdset
        self.cmdset.add_default(NpcBaseCmdSet, permanent=True)
