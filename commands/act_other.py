from commands.command import Command
from world.globals import DEFAULT_PROMPT_STRING
from world.map import Wormy
from world.utils.utils import is_wiz


class CmdPrompt(Command):
    """
    Customize your prompt

    Usage:
        prompt # displays current prompt
        prompt [prompt_string]

    [prompt_string] will parse the following tokens:

    %h - current health
    %H - max health
    %m - current magicka
    %M - current magicka
    %s - current stamina
    %S - max stamina
    %c - current carried weight
    %C - max carry weight
    %x - current speed
    %X - max speed
    """

    key = "prompt"

    def func(self):
        ch = self.caller
        args = self.args.strip()

        if not args:
            ch.msg(f"Your prompt is: {ch.db.prompt}")
            return

        if args.lower() == 'default':
            ch.db.prompt = DEFAULT_PROMPT_STRING
        else:
            ch.db.prompt = args
        ch.msg("prompt set")

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

    Minimum value is 5

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
            if size < 5:
                size = 5

            wormy = Wormy(ch, map_size_x=size, map_size_y=size, debug=debug)

        map_string = wormy.generate_map()
        ch.msg(map_string)