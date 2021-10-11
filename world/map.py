"""
Holds the class to generate a map
"""
from typing import Dict, Tuple
import numpy as np

from typeclasses.rooms.rooms import VALID_ROOM_SECTORS, Room
from typeclasses.characters import Character
from world.utils.db import search_roomdb
from world.globals import OPPOSITE_DIRECTION

_DEFAULT_MAP_SIZE = (5, 5)

_DIRECTION_MAPPING = {
    'north': np.array((0, -1)),
    'south': np.array((0, 1)),
    'east': np.array((1, 0)),
    'west': np.array((-1, 0))
}


class Wormy:
    """
    Creates a crawler that maps out nearby rooms based on position and thresholds.
    Generates a pretty string and returns back.

    Usage:
        ```python
        
        wormy = Wormy(ch.location)

        map_string = wormy.generate()

        # or
        
        # turn on debug mode    
        # caller_obj must support .msg() method

        map_string = wormy.generate(caller_obj=ch)

        ch.msg(map_string)
        ```
    
    """
    def __init__(self,
                 caller_obj: Character,
                 map_size_x=None,
                 map_size_y=None,
                 debug=False) -> None:

        self._caller_obj = caller_obj
        self._debug = debug

        # determine map size, either default or user supplied
        if (map_size_x is None) or (map_size_y is None):
            map_size: tuple = _DEFAULT_MAP_SIZE
        else:
            if map_size_x % 2 == 0:
                map_size_x += 1
            if map_size_y % 2 == 0:
                map_size_y += 1

            map_size: Tuple[int, int] = (map_size_x, map_size_y)

        # get center coords based on map size
        center_coords: Tuple[int, int] = tuple(map(lambda x: x // 2, map_size))

        # calculate space until edge of map
        self.edge_x: int = center_coords[0]
        self.edge_y: int = center_coords[1]

        # get current location object
        self.cur_location: Room = caller_obj.location

        # initalize empty map for drawing
        self._grid_map: np.ndarray = np.empty(map_size, dtype='<U8')

        # initalize starting coordinates
        self.current_coords: np.ndarray = np.array(center_coords)

        # initalize center coordinates in np array form
        self.center_coords = np.array(center_coords)

        # store static list of all exits within room
        self.current_room_exits = [
            exit_name
            for exit_name, rvnum in self.cur_location.db.exits.items()
            if (rvnum > 0) and exit_name not in ("up", "down")
        ]

    def debug_msg(self, *args):
        if not self._debug:
            return
        self._caller_obj.debug_msg(*args)

    def traverse(self,
                 exits: Dict[str, int],
                 previous_current_coordinates=None,
                 previous_exit_name=None):

        for exit_name, rvnum in exits.items():
            # check for exit conditions

            # skip exit that you came from
            if exit_name == previous_exit_name:
                continue

            # skip if no exit is found
            if rvnum < 0:
                continue

            # wormy can't traverse up or down right now :(
            if exit_name in ('up', 'down'):
                continue

            # update current coords based on exit name for next room
            previous_current_coordinates = self.current_coords.copy()
            self.current_coords += _DIRECTION_MAPPING[exit_name]
            self.debug_msg(self.cur_x, self.cur_y, exit_name)

            # if any value is below 0, we are out of bounds, ignore and reset coords to last valid position
            if np.any(self.current_coords < 0):
                self.debug_msg("triggered coords less than 0")
                self.current_coords = previous_current_coordinates.copy()
                continue

            # if any value is > (center_coords * 2), we are out of bounds, ignore and reset coords to last valid position
            if np.any(self.current_coords > (self.center_coords * 2)):
                self.debug_msg("triggered coords more than max")
                self.current_coords = previous_current_coordinates.copy()
                continue

            next_room = search_roomdb(vnum=rvnum)[rvnum]

            ######## do any drawing of the map below here #################

            self._grid_map[self.cur_x][self.cur_y] = VALID_ROOM_SECTORS[
                next_room['type']].symbol
            ############## do any drawing of the map above here ################

            self.debug_msg(exit_name, next_room['name'], rvnum,
                           self.current_coords, previous_current_coordinates,
                           next_room['type'])

            self.traverse(
                next_room['exits'],
                previous_current_coordinates=previous_current_coordinates,
                previous_exit_name=OPPOSITE_DIRECTION[exit_name])

            # returning from recursion means we finished worming through a particular
            # path.. resetting current_coords to starting point so the math aligns
            self.debug_msg("setting previous coordinates now...",
                           previous_current_coordinates)
            self.current_coords = previous_current_coordinates.copy()

        # exhausted all exits in room, roll back
        return

    @property
    def cur_x(self):
        return self.current_coords[1]

    @property
    def cur_y(self):
        return self.current_coords[0]

    def generate_map(self) -> str:
        # update center location
        self._grid_map[self.cur_x][self.cur_y] = "|M@|n"

        # begin traversing rooms
        self.traverse(self.cur_location.db.exits)

        # convert grid into prettyness
        map_string = ""
        map_size = self.center_coords * 2

        self.debug_msg(self._grid_map)
        for x in range(map_size[0] + 1):
            for y in range(map_size[1] + 1):
                grid_val = self._grid_map[x][y]

                if not grid_val:
                    map_string += f"{'':5}"
                else:
                    map_string += f"|c[{grid_val:1}|c]|n{'':2}"
            map_string += "\n\n"
        return map_string
