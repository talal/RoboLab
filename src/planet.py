#!/usr/bin/env python3

# Attention: Do not import the ev3dev.ev3 module in this file
from enum import Enum, unique
from typing import List, Optional, Tuple, Dict
import math

import random


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

# constants

BLOCKED_PATH = -1
DIRECTION_VERTICAL = 1
DIRECTION_HORIZONTAL = 2


class Path:
    def __init__(self, start: Tuple[Tuple[int, int], Direction], end: Tuple[Tuple[int, int], Direction],
                 weight: int):
        self.start = start
        self.end = end
        self.weight = weight

    def as_tuple(self):
        return (self.start, self.end), self.weight


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

        if new_path in self.nodes:
            return

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

    @staticmethod
    def get_random_direction(direction_type: int):

        if direction_type == DIRECTION_VERTICAL:
            if random.randint(0, 1) == 0:
                return Direction.SOUTH
            else:
                return Direction.NORTH
        elif direction_type == DIRECTION_HORIZONTAL:
            if random.randint(0, 1) == 0:
                return Direction.WEST
            else:
                return Direction.EAST
        else:
            raise Exception("direction_type is not DIRECTION_VERTICAL or DIRECTION_HORIZONTAL")

    def measure_direction(self, node_x: int, node_y: int, target_x: int, target_y: int) -> Direction:

        distance_x = abs(node_x - target_x)
        distance_y = abs(node_y - target_y)

        if distance_x > distance_y:
            if node_x < target_x:
                direction = Direction.EAST
            elif node_x > target_x:
                direction = Direction.WEST
            else:
                direction = self.get_random_direction(DIRECTION_VERTICAL)

        elif distance_y > distance_x:
            if node_y < target_y:
                direction = Direction.NORTH
            elif node_y > target_y:
                direction = Direction.SOUTH
            else:
                direction = self.get_random_direction(DIRECTION_HORIZONTAL)
        else:
            if target_y > node_y:
                direction = Direction.NORTH
            elif target_x > node_x:
                direction = Direction.EAST
            elif node_x > target_x:
                direction = Direction.WEST
            elif node_y > target_y:
                direction = Direction.SOUTH

        return direction

    def get_direction_to_go(self, node_x: int, node_y: int, target_x: int, target_y: int) -> Direction:

        direction_to_go = self.shortest_path((node_x, node_y), (target_x, target_y))
        if direction_to_go is None:
            direction_to_go = self.measure_direction(node_x, node_y, target_x, target_y)

        return direction_to_go

    def dijkstra(self, start, goal):

        shortest_distance = {}  # stores the minimum cost to reach that node
        track_visited_nodes = {}  # showes the path, that got us to this node
        not_seen_nodes = self.nodes.copy()
        pretty_big_number = 100000  # big number on unvisited nodes
        path = []  # optimal route

        start_node = Node(start)

        for node in not_seen_nodes:
            shortest_distance[node] = pretty_big_number
        shortest_distance[start] = 0

        while not_seen_nodes:
            min_distance_node = None

            for node in not_seen_nodes:
                if min_distance_node is None:
                    min_distance_node = node
                elif shortest_distance[node] < shortest_distance[min_distance_node]:
                    min_distance_node = node

    def shortest_path(self, start: Tuple[int, int], target: Tuple[int, int]) -> Optional[
        List[Tuple[Tuple[int, int], Direction]]]:
        """
        Returns a shortest path between two nodes

        Examples:
            shortest_path((0,0), (2,2)) returns: [((0, 0), Direction.EAST), ((1, 0), Direction.NORTH)]
            shortest_path((0,0), (1,2)) returns: None
        :param start: 2-Tuple
        :param target: 2-Tuple
        :return: 2-Tuple[List, Direction]
        """

        unvisited = self.nodes.copy()
        visited = dict()

        # predecessor
        pred = {start: None}
        start = Node(start[0], start[1])

        for node in self.nodes:
            if node == start:
                start = node

        while unvisited:
            min: Node = None
            for node in unvisited:
                if node in visited:
                    # could be an error
                    if min is None or visited[node] < visited[min]:
                        min = node
            if min is None:
                break
            unvisited.remove(min)
            current_weight = visited[min]

            paths = [min.path_to_north, min.path_to_east, min.path_to_west, min.path_to_south]
            i = 0
            for path in paths:

                direction = None
                if i == 0:
                    direction = Direction.NORTH
                elif i == 1:
                    direction = Direction.EAST
                elif i == 2:
                    direction = Direction.WEST
                elif i == 3:
                    direction = Direction.SOUTH

                if path.weight == BLOCKED_PATH:
                    continue

                weight = current_weight + path.weight
                if path.end not in visited or weight < visited[path.end]:
                    visited[path.end] = weight
                    pred[path.end[0]] = (min.coordinates, direction, current_weight)

                i += 1

        shortest_path = None
        if target in pred:
            shortest_path = []
            node = target
            while pred[node] is not None:
                shortest_path.insert(0, pred[node][0:2])
                node = pred[node][0]

        return shortest_path
