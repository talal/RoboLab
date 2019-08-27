from enum import unique, Enum


@unique
class Direction(Enum):
    NORTH = "N"
    EAST = "E"
    SOUTH = "S"
    WEST = "W"


@unique
class PathStatus(Enum):
    BLOCKED = "blocked"
    FREE = "free"


def flip_direction(direction: Direction) -> Direction:
    return {
        Direction.NORTH: Direction.SOUTH,
        Direction.EAST: Direction.WEST,
        Direction.SOUTH: Direction.NORTH,
        Direction.WEST: Direction.EAST,
    }[direction]


def degrees_to_nearest_direction(degrees: int) -> Direction:
    if degrees > 360:
        n = degrees % 360
        degrees -= n * 360

    degrees /= 90
    degrees = round(degrees)
    degrees %= 4

    return {0: Direction.NORTH, 1: Direction.EAST, 2: Direction.SOUTH, 3: Direction.WEST}[degrees]


def direction_to_degrees(direction: Direction) -> int:
    return {Direction.NORTH: 0, Direction.EAST: 90, Direction.SOUTH: 180, Direction.WEST: 270}[
        direction
    ]


def make_scanned_directions_relative(scanned_directions, current_direction):
   return [
        degrees_to_nearest_direction(
            make_direction_relative(d, current_direction)
        )
        for d in scanned_directions
    ]

def make_direction_relative(direction, current_direction):
    opposite_direction = flip_direction(current_direction)
    return direction_to_degrees(direction) + direction_to_degrees(opposite_direction)
