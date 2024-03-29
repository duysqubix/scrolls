"""
Holds the class to generate a map
"""
import json
from typing import Any, Dict, Optional, Tuple, List, Dict
import numpy as np

from typeclasses.rooms.rooms import VALID_ROOM_SECTORS, Room
from typeclasses.characters import Character
from world.utils.db import search_roomdb
from world.utils.utils import DBDumpEncoder
from world.globals import OPPOSITE_DIRECTION

_DEFAULT_MAP_SIZE: Tuple[int, int] = (5, 5)

_DIRECTION_MAPPING: Dict[str, np.ndarray] = {
    'north': np.array((0, -2)),
    'south': np.array((0, 2)),
    'east': np.array((2, 0)),
    'west': np.array((-2, 0))
}

_HORIZONTAL_PATH_ICON: str = '---'
_VERTICAL_PATH_ICON: str = ' | '
_UP_ICON: str = '|r+  |n'
_DOWN_ICON: str = '|r  ‾|n'


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
    @staticmethod
    def calculate_map_size(map_size_x, map_size_y) -> Tuple[int, int]:
        # determine map size, either default or user supplied
        if (map_size_x is None) or (map_size_y is None):
            map_size_x = _DEFAULT_MAP_SIZE[0]
            map_size_y = _DEFAULT_MAP_SIZE[1]
        else:
            if map_size_x % 2 == 0:
                map_size_x += 1
            if map_size_y % 2 == 0:
                map_size_y += 1

        map_size_x += 4
        map_size_y += 4

        return (map_size_x, map_size_y)

    @staticmethod
    def calculate_center_coordinates(map_size_x,
                                     map_size_y) -> Tuple[int, int]:
        """calculates center coordinates based on map_size"""

        if map_size_x != map_size_y:
            raise ValueError("map_size_x and map_size_y are different, %s" %
                             str((map_size_x, map_size_y)))

        return tuple(map(lambda x: x // 2, (map_size_x, map_size_y)))

    @staticmethod
    def initialize_grid_map(max_x, max_y) -> List[List[Dict[str, Any]]]:
        # initalize empty map for drawing
        grid_map: List[List[Dict[str, Any]]] = list()

        for _ in range(max_x):
            tmp_row = list()
            for _ in range(max_y):
                tmp_row.append({
                    'symbol': '',
                    'up': False,
                    'down': False,
                    'south': False,
                    'east': False,
                    'west': False,
                    'north': False
                })
            grid_map.append(tmp_row)
        return grid_map

    def __init__(self,
                 caller_obj: Character,
                 map_size_x: Optional[int] = None,
                 map_size_y: Optional[int] = None,
                 debug=False) -> None:

        self._caller_obj: Character = caller_obj
        self._debug: bool = debug

        map_size: Tuple[int, int] = Wormy.calculate_map_size(
            map_size_x, map_size_y)

        # get center coords based on map size
        center_coords: Tuple[int, int] = Wormy.calculate_center_coordinates(
            map_size[0], map_size[1])

        # get current location object
        self.cur_location: Room = caller_obj.location

        # initalize empty map for drawing
        self._grid_map: List[List[Dict[str, Any]]] = Wormy.initialize_grid_map(
            map_size[0], map_size[1])

        # initalize starting coordinates
        self.current_coords: np.ndarray = np.array(center_coords,
                                                   dtype=np.int32)

        # initalize center coordinates in np array form
        self.center_coords = np.array(center_coords, dtype=np.int32)

        self.debug_msg(
            json.dumps(
                {
                    "map_size_x": map_size_x,
                    "map_size_y": map_size_y,
                    "center_coords": center_coords,
                    "caller_obj": str(caller_obj),
                    "supplied_map_size": map_size
                },
                cls=DBDumpEncoder))

    def debug_msg(self, msg):
        """helper function to send caller_obj debug messages if enabled"""
        if not self._debug:
            return
        self._caller_obj.msg(str(msg))

    def traverse(self,
                 exits: Dict[str, int],
                 previous_current_coordinates: Optional[np.ndarray] = None,
                 previous_exit_name: Optional[str] = None,
                 _debug_indent: int = 0) -> None:
        """
        Main recursive method that 'crawls' into other rooms and
        dynamically generates the map, stores initial data in a grid-like
        data type which is a python-native list of lists of dictionaries
        """
        for exit_name, rvnum in exits.items():
            # check for exit conditions

            # skip exit that you came from
            if exit_name == previous_exit_name:
                continue

            # skip if no exit is found
            if rvnum < 0:
                continue

            # wormy can't traverse up or down right now :(
            # but we can indicate it!
            if exit_name in ('up', 'down'):
                self.debug_msg(("FOUND A INVLAID EXIT: ", exit_name,
                                self.cur_x, self.cur_y))
                if exit_name == 'up':
                    self._grid_map[self.cur_x][self.cur_y]['up'] = True
                if exit_name == 'down':
                    self._grid_map[self.cur_x][self.cur_y]['down'] = True

                continue

            self._grid_map[self.cur_x][self.cur_y][exit_name] = True

            # update current coords based on exit name for next room
            previous_current_coordinates: np.ndarray = self.current_coords.copy(
            )
            self.current_coords += _DIRECTION_MAPPING[exit_name]

            # if any value is below 0, we are out of bounds, ignore and reset coords to last valid position
            if np.any(self.current_coords < 0):
                self.debug_msg("triggered coords less than 0; off map")
                self.current_coords = previous_current_coordinates.copy()
                continue

            # if any value is > (center_coords * 2), we are out of bounds, ignore and reset coords to last valid position
            if np.any(self.current_coords > (self.center_coords * 2)):
                self.debug_msg("triggered coords more than max")
                self.current_coords = previous_current_coordinates.copy()
                continue

            next_room: Dict[str, Any] = search_roomdb(vnum=rvnum)[rvnum]

            ######## do any drawing of the map below here #################

            self._grid_map[self.cur_x][self.cur_y][
                'symbol'] = VALID_ROOM_SECTORS[next_room['type']].symbol

            ############## do any drawing of the map above here ################
            self.debug_msg(("******" * _debug_indent) + json.dumps(
                {
                    exit_name: {
                        "next_room": next_room['name'],
                        "rvnum": rvnum,
                        "previous_coordinates": {
                            "x": previous_current_coordinates[0],
                            "y": previous_current_coordinates[1]
                        },
                        "direction_value": _DIRECTION_MAPPING[exit_name],
                        "current_coordinates": {
                            "x": self.cur_x,
                            "y": self.cur_y
                        },
                        "next_room_type": next_room['type'],
                        "symbol": VALID_ROOM_SECTORS[next_room['type']].symbol
                    }
                },
                cls=DBDumpEncoder))

            self.traverse(
                next_room['exits'],
                previous_current_coordinates=previous_current_coordinates,
                previous_exit_name=OPPOSITE_DIRECTION[exit_name],
                _debug_indent=(_debug_indent + 1))

            # returning from recursion means we finished worming through a particular
            # path.. resetting current_coords to starting point so the math aligns
            self.debug_msg(
                f"Path complete, resetting coordinates back to room {rvnum} at {previous_current_coordinates}"
            )
            self.current_coords = previous_current_coordinates.copy()

        # exhausted all exits in room, roll back
        return

    @property
    def cur_x(self) -> np.int32:
        return self.current_coords[1]

    @property
    def cur_y(self) -> np.int32:
        return self.current_coords[0]

    def generate_map(self) -> str:
        # update center location
        self._grid_map[self.cur_x][self.cur_y]['symbol'] = "|M@|n"
        # begin traversing rooms
        self.traverse(self.cur_location.db.exits)

        map_string: str = ""
        map_size: np.ndarray = self.center_coords * 2

        # fill in paths between rooms here based on current grid
        for x in range(map_size[0] + 1):
            for y in range(map_size[1] + 1):
                grid_val: Dict[str, Any] = self._grid_map[x][y]

                # ignore empty ones for now
                if grid_val['symbol'] == '':
                    continue

                # get all exits in that came out positive
                exits: List[str] = [
                    exit_name for exit_name, exists in grid_val.items()
                    if exists is True  #and exit_name not in ('up', 'down')
                ]

                # map write '-', or '|' depending on exit directions relatively

                for exit_ in exits:
                    north_offset = x - 1
                    south_offset = x + 1
                    east_offset = y + 1
                    west_offset = y - 1

                    self.debug_msg((exit_, north_offset, south_offset,
                                    east_offset, west_offset, map_size + 1))

                    if exit_ == 'north' and north_offset > 0:
                        self.debug_msg((north_offset, y, exit_))
                        self._grid_map[north_offset][y][
                            'symbol'] = _VERTICAL_PATH_ICON

                    if exit_ == 'south' and south_offset < map_size[0] + 1:
                        self.debug_msg((south_offset, y, exit_))
                        self._grid_map[south_offset][y][
                            'symbol'] = _VERTICAL_PATH_ICON

                    if exit_ == 'east' and east_offset < map_size[0] + 1:
                        self.debug_msg((x, east_offset, exit_))

                        self._grid_map[x][east_offset][
                            'symbol'] = _HORIZONTAL_PATH_ICON

                    if exit_ == 'west' and west_offset > 0:
                        self.debug_msg((x, west_offset, exit_))

                        self._grid_map[x][west_offset][
                            'symbol'] = _HORIZONTAL_PATH_ICON

                    if exit_ == 'up' and (north_offset > 0
                                          and east_offset < map_size[0] + 1):
                        self.debug_msg((north_offset, east_offset, exit_))

                        self._grid_map[north_offset][east_offset][
                            'symbol'] = _UP_ICON

                    if exit_ == 'down' and (west_offset > 0 and
                                            south_offset < map_size[0] + 1):
                        self.debug_msg((north_offset, east_offset, exit_))
                        self._grid_map[south_offset][west_offset][
                            'symbol'] = _DOWN_ICON

        # convert grid into prettyness string
        for x in range(map_size[0] + 1):
            for y in range(map_size[1] + 1):
                grid_val: Dict[str, Any] = self._grid_map[x][y]

                if grid_val['symbol'] == '':
                    map_string += f"{'':3}"
                else:
                    if grid_val['symbol'] in (_VERTICAL_PATH_ICON,
                                              _HORIZONTAL_PATH_ICON, _UP_ICON,
                                              _DOWN_ICON):
                        map_string += grid_val['symbol']
                    else:
                        map_string += f"|c[{grid_val['symbol']:1}|c]|n"

            map_string += "\n"
        return map_string
