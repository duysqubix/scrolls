from evennia import search_object, logger
from commands.command import Command
from typeclasses.rooms.rooms import Room
_MOVEMENT_HELP = """

Attempt to move in a cardinal direction from
current location. 

Valid directions:
    - north
    - south
    - east
    - west
    - up
    - down
"""

_ERR_MOVEMENT = "You can't go that way."


class _CmdMove(Command):
    __doc__ = _MOVEMENT_HELP

    def func(self):
        ch = self.caller
        cur_room = ch.location
        exit = cur_room.db.exits[self.key]
        if exit < 0:
            ch.msg(_ERR_MOVEMENT)
            return

        # double check to make sure destination room actually exists
        room = search_object(str(exit), typeclass=Room)
        ch.msg("{}{}".format(exit, room))
        if not room:
            logger.log_errmsg(
                "Attempting to move to a valid exit vnum, but room doesn't exist"
            )
            ch.msg(_ERR_MOVEMENT)
            return
        room = room[0]

        # special condition if ch is in redit
        if ch.ndb._redit:
            ch.ndb._redit.__init__(ch, exit)
        # valid, lets move
        ch.move_to(room)


class CmdNorth(_CmdMove):
    key = 'north'
    aliases = ['n']


class CmdSouth(_CmdMove):
    key = 'south'
    aliases = ['s']


class CmdWest(_CmdMove):
    key = 'west'
    aliases = ['w']


class CmdEast(_CmdMove):
    key = 'east'
    aliases = ['e']


class CmdUp(_CmdMove):
    key = 'up'
    aliases = ['u']


class CmdDown(_CmdMove):
    key = 'down'
    aliases = ['d']