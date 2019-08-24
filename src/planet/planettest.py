#!/usr/bin/env python3

import unittest

from planet.planet import Direction, Planet


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
        self.planet.add_path(((0, 0), Direction.EAST), ((1, 0), Direction.WEST), 1)
        self.planet.add_path(((0, 1), Direction.NORTH), ((0, 2), Direction.SOUTH), 1)
        self.planet.add_path(((0, 2), Direction.NORTH), ((0, 3), Direction.SOUTH), 1)
        self.planet.add_path(((0, 2), Direction.EAST), ((2, 2), Direction.WEST), 3)
        self.planet.add_path(((2, 2), Direction.NORTH), ((0, 3), Direction.EAST), 6)
        self.planet.add_path(((0, 3), Direction.NORTH), ((0, 3), Direction.WEST), 1)
        self.planet.add_path(((1, 0), Direction.NORTH), ((2, 2), Direction.SOUTH), 8)

    def test_integrity(self):
        """
        This test should check that the dictionary returned by "planet.get_paths()" matches the expected structure
        """
        expected = {
            (0, 0): {
                Direction.EAST: ((1, 0), Direction.WEST, 1),
                Direction.NORTH: ((0, 1), Direction.SOUTH, 1),
                Direction.WEST: ((0, 1), Direction.WEST, 1),
            },
            (1, 0): {
                Direction.WEST: ((0, 0), Direction.EAST, 1),
                Direction.NORTH: ((2, 2), Direction.SOUTH, 8),
            },
            (0, 1): {
                Direction.WEST: ((0, 0), Direction.WEST, 1),
                Direction.SOUTH: ((0, 0), Direction.NORTH, 1),
                Direction.NORTH: ((0, 2), Direction.SOUTH, 1),
            },
            (0, 2): {
                Direction.EAST: ((2, 2), Direction.WEST, 3),
                Direction.SOUTH: ((0, 1), Direction.NORTH, 1),
                Direction.NORTH: ((0, 3), Direction.SOUTH, 1),
            },
            (2, 2): {
                Direction.NORTH: ((0, 3), Direction.EAST, 6),
                Direction.WEST: ((0, 2), Direction.EAST, 3),
                Direction.SOUTH: ((1, 0), Direction.NORTH, 8),
            },
            (0, 3): {
                Direction.WEST: ((0, 3), Direction.NORTH, 1),
                Direction.EAST: ((2, 2), Direction.NORTH, 6),
                Direction.NORTH: ((0, 3), Direction.WEST, 1),
                Direction.SOUTH: ((0, 2), Direction.NORTH, 1),
            },
        }
        got = self.planet.get_paths()
        self.assertEqual(got, expected)

    def test_empty_planet(self):
        """
        This test should check that an empty planet really is empty
        """
        expected = {}
        empty_planet = Planet()
        got = empty_planet.get_paths()
        self.assertEqual(got, expected)

    def test_target(self):
        """
        This test should check that the shortest-path algorithm implemented works.

        Requirement: Minimum distance is three nodes (two paths in list returned)
        """
        expected = [((0, 0), Direction.NORTH), ((0, 1), Direction.NORTH), ((0, 2), Direction.EAST)]
        expected2 = [((0, 0), Direction.WEST), ((0, 1), Direction.NORTH), ((0, 2), Direction.EAST)]
        got = self.planet.shortest_path((0, 0), (2, 2))
        self.assertTrue((got == expected) or (got == expected2))

    def test_target_not_reachable(self):
        """
        This test should check that a target outside the map or at an unexplored node is not reachable
        """
        expected = None
        got = self.planet.shortest_path((0, 0), (1, 2))
        self.assertEqual(got, expected)

    def test_same_length(self):
        """
        This test should check that the shortest-path algorithm implemented also can return alternatives with the
        same cost (weights)

        Requirement: Minimum of two paths with same cost exists, only one is returned by the logic implemented
        """
        expected = [((0, 0), Direction.NORTH), ((0, 1), Direction.NORTH), ((0, 2), Direction.EAST)]
        expected2 = [((0, 0), Direction.WEST), ((0, 1), Direction.NORTH), ((0, 2), Direction.EAST)]
        got = self.planet.shortest_path((0, 0), (2, 2))
        self.assertTrue((got == expected) or (got == expected2))

    def test_target_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target nearby

        Result: Target is reachable
        """
        expected = [((0, 0), Direction.NORTH), ((0, 1), Direction.NORTH)]
        got = self.planet.shortest_path((0, 0), (0, 2))
        self.assertEqual(got, expected)

    def test_target_not_reachable_with_loop(self):
        """
        This test should check that the shortest-path algorithm does not get stuck in a loop between two points while
        searching for a target not reachable nearby

        Result: Target is not reachable
        """
        expected = [((0, 2), Direction.EAST)]
        got = self.planet.shortest_path((0, 2), (2, 2))
        self.assertEqual(got, expected)


if __name__ == "__main__":
    unittest.main()
