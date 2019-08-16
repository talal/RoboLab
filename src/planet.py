#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import Enum, unique
from typing import List, Optional, Tuple, Dict


@unique
class Direction(Enum):
    """ Directions in shortcut """
    NORTH = "N"
    EAST = "E"
    SOUTH = "S"
    WEST = "W"


Weight = int
""" 
Weight of a given path (received from the server)

Value:  -1 if blocked path
        >0 for all other paths
        never 0
"""

BLOCKED_PATH = -1


class Path:
    def __init__(self, start: Tuple[Tuple[int, int], Direction], end: Tuple[Tuple[int, int], Direction],
                 weight: int):
        self.start = start
        self.end = end
        self.weight = weight

    def as_tuple(self):
        return self.start, self.end, self.weight


class Node:
    def __init__(self, x_coordinate: int, y_coordinate: int):
        self.coordinates = x_coordinate, y_coordinate

        # path array to each direction

        self.path_to_north = None
        self.path_to_west = None
        self.path_to_east = None
        self.path_to_south = None

    def add_path(self, direction: Direction, path: Path):
        if direction == Direction.NORTH:
            self.path_to_north = path
        elif direction == Direction.WEST:
            self.path_to_west = path
        elif direction == Direction.EAST:
            self.path_to_east = path
        else:
            self.path_to_south = path

    def get_paths(self) -> Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]:

        all_paths = dict()

        all_paths[Direction.NORTH] = self.path_to_north
        all_paths[Direction.WEST] = self.path_to_west
        all_paths[Direction.EAST] = self.path_to_east
        all_paths[Direction.SOUTH] = self.path_to_south

        return all_paths


class Planet:
    """
    Contains the representation of the map and provides certain functions to manipulate or extend
    it according to the specifications
    """

    def __init__(self):
        """ Initializes the data structure """

        # contains all nodes of the planet
        self.nodes = set()

        # the target point provided by the mothership
        self.target = None

    def add_path(self, start: Tuple[Tuple[int, int], Direction], target: Tuple[Tuple[int, int], Direction],
                 weight: int):
        """
         Adds a bidirectional path defined between the start and end coordinates to the map and assigns the weight to it

        Example:
            add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST), 1)
        :param start: 2-Tuple
        :param target:  2-Tuple
        :param weight: Integer
        :return: void
        """

        # YOUR CODE FOLLOWS (remove pass, please!)

        new_path = Path(start, target, weight)
        self.nodes.add(new_path)

    def get_paths(self) -> Dict[Tuple[int, int], Dict[Direction, Tuple[Tuple[int, int], Direction, Weight]]]:
        """
        Returns all paths

        Example:
            {
                (0, 3): {
                    Direction.NORTH: ((0, 3), Direction.WEST, 1),
                    Direction.EAST: ((1, 3), Direction.WEST, 2)
                },
                (1, 3): {
                    Direction.WEST: ((0, 3), Direction.EAST, 2),
                    ...
                },
                ...
            }
        :return: Dict
        """

        # YOUR CODE FOLLOWS (remove pass, please!)

        all_paths = dict()

        for node in self.nodes:
            all_paths[node.coordinates] = node.get_paths()

        return all_paths

    def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> Optional[List[Tuple[Tuple[int, int], Direction]]]:
        """
        Returns a shortest path between two nodes

        Examples:
            shortest_path((0,0), (2,2)) returns: [((0, 0), Direction.EAST), ((1, 0), Direction.NORTH)]
            shortest_path((0,0), (1,2)) returns: None
        :param start: 2-Tuple
        :param target: 2-Tuple
        :return: 2-Tuple[List, Direction]
        """

        # YOUR CODE FOLLOWS (remove pass, please!)
        pass
