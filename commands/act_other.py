from commands.command import Command
from world.map import Wormy
from world.utils.utils import is_wiz


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
    Map size must be an odd number, if an even number is supplied
    it will round to nearest number up.

    Usage:
        map
        map 5 # create map size of 5x5
        map 7 # create map size of 7x7

    Wizes:
        map 5 true/false # will display debug information if wiz
    """

    key = "map"

    def func(self):
        ch = self.caller
        args = self.args.strip().split()
        debug = False

        if len(args) < 1:
            wormy = Wormy(ch, debug=debug)
        else:
            if len(args) == 2 and is_wiz(ch):
                debug = True if eval(args[1].capitalize()) is True else False

            try:
                size = int(args[0])
            except ValueError:
                ch.msg("Invalid map size")
                return

            if size > 10:
                ch.msg("Map size too big")
                return

            wormy = Wormy(ch, map_size_x=size, map_size_y=size, debug=debug)

        map_string = wormy.generate_map()
        ch.msg(map_string)