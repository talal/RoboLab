import math
from typing import Tuple, List

from logger import get_logger
from robot.sensors.color import RGBColor
from utils.common import (
    Direction,
    PathStatus,
    direction_to_degrees,
    flip_direction,
    degrees_to_nearest_direction,
)


class Odometry:
    def __init__(self):
        # in cm
        self.wheel_diameter = 5.6
        self.wheel_distance = 11.8
        self.planet_grid_unit = 50

        self.logger = get_logger(__name__)
        self.__current_coordinates: Tuple[int, int] = None
        self.__current_direction: Direction = None
        self.__current_node_color: RGBColor = None
        self.__previous_coordinates: Tuple[int, int] = None
        self.__previous_direction: Direction = None
        self.__previous_node_color: RGBColor = None

    @property
    def current_coordinates(self):
        return self.__current_coordinates

    @current_coordinates.setter
    def current_coordinates(self, value: Tuple[int, int]):
        self.__current_coordinates = value

    @property
    def current_direction(self):
        return self.__current_direction

    @current_direction.setter
    def current_direction(self, value: Direction):
        self.__current_direction = value

    def set_start(self, start: Tuple[Tuple[int, int], Direction]):
        self.current_coordinates = start[0]
        self.current_direction = start[1]

    @property
    def previous_coordinates(self):
        return self.__previous_coordinates

    @previous_coordinates.setter
    def previous_coordinates(self, value: Tuple[int, int]):
        self.__previous_coordinates = value

    @property
    def previous_direction(self):
        return self.__previous_direction

    @previous_direction.setter
    def previous_direction(self, value: Direction):
        self.__previous_direction = value

    def set_end(self, end: Tuple[Tuple[int, int], Direction]):
        self.previous_coordinates = end[0]
        self.previous_direction = end[1]

    @property
    def current_node_color(self):
        return self.__current_node_color

    @current_node_color.setter
    def current_node_color(self, value: RGBColor):
        self.__current_node_color = value

    @property
    def previous_node_color(self):
        return self.__previous_node_color

    @previous_node_color.setter
    def previous_node_color(self, value: RGBColor):
        self.__previous_node_color = value

    @staticmethod
    def __radian_to_degree(radian):
        return round((radian * 57.29578), 3)

    @staticmethod
    def __degree_to_radian(degree):
        return round((degree / 57.29578), 3)

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

    def handle(
        self,
        current_direction: Direction,
        path_status: PathStatus,
        positions_list: List[Tuple[int, int]],
    ):
        self.previous_node_color = self.current_node_color
        self.previous_coordinates = self.current_coordinates
        self.previous_direction = self.current_direction
        self.logger.debug(
            f"Odometry: previous direction={self.previous_direction} and coordinates={self.previous_coordinates}"
        )

        if path_status == PathStatus.BLOCKED:
            self.current_direction = flip_direction(self.current_direction)
            return

        gamma = self.__degree_to_radian(direction_to_degrees(current_direction))
        delta_x = 0
        delta_y = 0
        for i, positions in enumerate(positions_list):
            if i == 0:
                continue
            previous_positions = positions_list[i - 1]
            dl = self.__position_to_d(positions[0] - previous_positions[0])
            dr = self.__position_to_d(positions[1] - previous_positions[1])
            alpha, beta = self.__calculate_alpha_and_beta(dl, dr)
            if alpha == 0:
                s = dl
            else:
                s = self.__calculate_s(dl, dr, alpha, beta)
            delta_x += self.__calculate_delta_x(gamma, beta, s)
            delta_y += self.__calculate_delta_y(gamma, beta, s)
            # new gamma calculation needs to be at the end, after all the
            # other calculations have been done using the old gamma value
            gamma += alpha

        previous_direction_degrees = direction_to_degrees(self.previous_direction)
        new_direction_degrees = self.__radian_to_degree(gamma) + previous_direction_degrees
        new_direction = degrees_to_nearest_direction(new_direction_degrees)

        new_coordinates = (
            round(self.previous_coordinates[0] + (delta_x / self.planet_grid_unit)),
            round(self.previous_coordinates[1] + (delta_y / self.planet_grid_unit)),
        )

        self.current_coordinates = new_coordinates
        self.current_direction = new_direction

        self.logger.debug(
            f"Odometry: current direction={self.current_direction} and coordinates={self.current_coordinates}"
        )
