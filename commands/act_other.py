from commands.command import Command
from world.map import Wormy


class CmdTitle(Command):
    """
    Set your title to whatever you would like.

    Usage:
        title clear # clears title
        title , the bloody warrior
        title , the |rbloody|n warrior
    """

    key = 'title'

    def func(self):
        ch = self.caller

        args = self.args.strip()
        if not args:
            ch.msg('What do you want to your title to be?')
            return

        if args == 'clear':
            ch.attrs.title.value = ""
        else:
            ch.attrs.title.value = args
        ch.msg("Title set.")


class CmdMap(Command):
    """
    Displays a map of your surroundings.

    Usage:
        map
    """

    key = "map"

    def func(self):
        ch = self.caller

        wormy = Wormy(ch, debug=False)

        map_string = wormy.generate_map()
        ch.msg(map_string)