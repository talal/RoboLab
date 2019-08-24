import math
from typing import Tuple, List

from planet.planet import Direction, PathStatus
from robot.sensors.color import RGBColor


class Odometry:
    def __init__(self):
        # in cm
        self.wheel_diameter = 5.6
        self.wheelbase = 10.6
        self.wheel_distance = 11.8

        self.__start_coordinates: Tuple[int, int] = None
        self.__start_direction: Direction = None
        self.__end_coordinates: Tuple[int, int] = None
        self.__end_direction: Direction = None
        self.__node_color: RGBColor = None
        self.__previous_node_color: RGBColor = None

    @property
    def start_coordinates(self):
        return self.__start_coordinates

    @start_coordinates.setter
    def start_coordinates(self, value: Tuple[int, int]):
        self.__start_coordinates = value

    @property
    def start_direction(self):
        return self.__start_direction

    @start_direction.setter
    def start_direction(self, value: Direction):
        self.__start_direction = value

    def set_start(self, start: Tuple[Tuple[int, int], Direction]):
        self.start_coordinates = start[0]
        self.start_direction = start[1]

    @property
    def end_coordinates(self):
        return self.__end_coordinates

    @end_coordinates.setter
    def end_coordinates(self, value: Tuple[int, int]):
        self.__end_coordinates = value

    @property
    def end_direction(self):
        return self.__end_direction

    @end_direction.setter
    def end_direction(self, value: Direction):
        self.__end_direction = value

    def set_end(self, end: Tuple[Tuple[int, int], Direction]):
        self.end_coordinates = end[0]
        self.end_direction = end[1]

    @staticmethod
    def __flip_direction(direction: Direction):
        return {
            Direction.NORTH: Direction.SOUTH,
            Direction.EAST: Direction.WEST,
            Direction.SOUTH: Direction.NORTH,
            Direction.WEST: Direction.EAST,
        }[direction]

    @staticmethod
    def __radian_to_degree(radian):
        return round((radian * 57.29578), 3)

    def __position_to_d(self, position):
        return (position / 360) * math.pi * self.wheel_diameter

    def __calculate_alpha_and_beta(self, dl, dr):
        alpha = (dr - dl) / self.wheel_distance
        beta = alpha / 2
        return alpha, beta

    @staticmethod
    def __calculate_s(dl, dr, alpha, beta):
        return ((dr + dl) / alpha) * math.sin(beta)

    @staticmethod
    def __calculate_delta_x(old_gamma, beta, s):
        return (-math.sin(old_gamma + beta)) * s

    @staticmethod
    def __calculate_delta_y(old_gamma, beta, s):
        return (math.cos(old_gamma + beta)) * s

    @staticmethod
    def __calculate_new_gamma(old_gamma, alpha):
        return old_gamma + alpha

    def handle(
        self, node_color: RGBColor, path_status: PathStatus, positions_list: List[Tuple[int, int]]
    ):
        gamma = 0
        s = 0
        delta_x = 0
        delta_y = 0
        for i, positions in enumerate(positions_list, 1):
            previous_positions = positions_list[i - 1]
            dl = self.__position_to_d(positions[0] - previous_positions[0])
            dr = self.__position_to_d(positions[1] - previous_positions[1])
            alpha, beta = self.__calculate_alpha_and_beta(dl, dr)
            if alpha == 0:
                s += dl
            else:
                s += self.__calculate_s(dl, dr, alpha, beta)
            delta_x += self.__calculate_delta_x(gamma, beta, s)
            delta_y += self.__calculate_delta_y(gamma, beta, s)
            gamma = self.__calculate_new_gamma(gamma, alpha)

        print(f"gamma={gamma}, s={s}, delta_x={delta_x}, delta_y={delta_y}")
