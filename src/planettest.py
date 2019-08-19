#!/usr/bin/env python3

import unittest
from planet import Direction, Planet


class ExampleTestPlanet(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        +--+
        |  |
        +-0,3------+
           |       |
          0,2-----2,2 (target)
           |      /
        +-0,1    /
        |  |    /
        +-0,0-1,0
           |
        (start)

        """
        # Initialize your data structure here
        self.planet = Planet()
        self.planet.add_path(((0, 0), Direction.NORTH), ((0, 1), Direction.SOUTH), 1)
        self.planet.add_path(((0, 1), Direction.WEST), ((0, 0), Direction.WEST), 1)

    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        self.assertIsNone(self.planet.shortest_path((0, 0), (1, 2)))


class RoboLabPlanetTests(unittest.TestCase):
    def setUp(self):
        """
        Instantiates the planet data structure and fills it with paths

        MODEL YOUR TEST PLANET HERE (if you'd like):

        """
        # Initialize your data structure here
        self.planet = Planet()
        # self.planet.add_path(...)
        self.planet.add_path((0, 0), (1, 0), 1)
        self.planet.add_path((1, 0), (1, 1), 2)
        self.planet.add_path((1, 1), (0, 1), 3)
        self.planet.add_path((0, 1), (0, 0), 4)

    def test_integrity(self):
        """
        This test should check that the dictionary returned by "planet.get_paths()" matches the expected structure
        """
        self.fail('implement me!')

    def test_empty_planet(self):
        """
        This test should check that an empty planet really is empty
        """
        self.fail('implement me!')

    def test_target(self):
        """
        This test should check that the shortest-path algorithm implemented works.

        Requirement: Minimum distance is three nodes (two paths in list returned)
        """

        direction = self.planet.get_direction_to_go(0, 0, 1, 1)


    def test_target_not_reachable(self):
        """
        This test should check that a target outside the map or at an unexplored node is not reachable
        """

        self.planet.add_path((10, 10), (20, 20), 10)

        self.assertEqual(None, self.planet.shortest_path((0, 0), (20, 20)))

    def test_same_length(self):
        """
        This test should check that the shortest-path algorithm implemented also can return alternatives with the
        same cost (weights)

        Requirement: Minimum of two paths with same cost in list returned
        """
        self.fail('implement me!')

    def test_target_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target nearby

        Result: Target is reachable
        """
        self.planet.add_path((10, 10), (20, 20), 10)

        self.assertNotEqual(None, self.planet.shortest_path((0, 0), (1, 1)))

    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        self.fail('implement me!')

    def test_measure_direction(self):
        direction = self.planet.measure_direction(5, 7, 1, 10)
        self.assertEqual(direction, Direction.WEST)

        direction = self.planet.measure_direction(1, 1, 9, 1)
        self.assertEqual(direction, Direction.EAST)

        direction = self.planet.measure_direction(1, 1, 2, 10)
        self.assertEqual(direction, Direction.NORTH)

        direction = self.planet.measure_direction(1, 10, 2, 1)
        self.assertEqual(direction, Direction.SOUTH)


if __name__ == "__main__":
    unittest.main()
