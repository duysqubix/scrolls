"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

from evennia import default_cmds, CmdSet
from evennia.commands.default.building import CmdDig as OrigCmdDig
import commands.informative as info
import commands.act_item as act_item
import commands.act_movement as act_mov
import commands.wiz as wiz
from commands.wiz import CmdBookLoad, CmdDBLoad
from world.globals import BUILDER_LVL


class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        self.add(info.CmdAffect())
        self.add(info.CmdLook())
        self.add(info.CmdScore())
        self.add(info.CmdRead())
        self.add(info.CmdInventory())
        self.add(info.CmdEquipment())
        self.add(info.CmdTime())
        self.add(info.CmdWho())

        self.add(act_item.CmdPut())
        self.add(act_item.CmdGet())
        self.add(act_item.CmdWear())
        self.add(act_item.CmdRemove())
        self.add(act_item.CmdDrop())
        self.add(act_item.CmdWield())

        # movement commands
        self.add(act_mov.CmdNorth())
        self.add(act_mov.CmdSouth())
        self.add(act_mov.CmdEast())
        self.add(act_mov.CmdWest())
        self.add(act_mov.CmdUp())
        self.add(act_mov.CmdDown())


class BuilderCmdSet(CmdSet):
    """
    The command sets for builders
    """
    key = "Builder"

    def at_cmdset_creation(self):
        self.add(wiz.CmdCharacterGen())
        self.add(wiz.CmdLoad())
        self.add(wiz.CmdOEdit())
        self.add(wiz.CmdREdit())
        self.add(wiz.CmdRestore())
        self.add(wiz.CmdOList())
        self.add(wiz.CmdRList())
        self.add(wiz.CmdZList())
        self.add(wiz.CmdHolyLight())
        self.add(wiz.CmdGoto())
        self.add(wiz.CmdWizHelp)


class ImmCmdSet(CmdSet):
    """
    command sets for immortals
    """
    key = "Immortal"

    def at_cmdset_creation(self):
        self.add(wiz.CmdPurge())


class WizCmdSet(CmdSet):
    """
    commands for wizards
    """
    key = "Wizard"

    def at_cmdset_creation(self):
        self.add(wiz.CmdZoneSet())
        self.add(wiz.CmdZEdit())


class GodCmdSet(CmdSet):
    """
    commands for super user only
    """
    key = "God"

    def at_cmdset_creation(self):
        self.add(wiz.CmdDBDump())
        self.add(wiz.CmdBookLoad())
        self.add(wiz.CmdDBLoad())
        self.add(wiz.CmdLanguageUpdate())


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
