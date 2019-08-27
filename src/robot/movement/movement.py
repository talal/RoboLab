import time
from typing import Tuple, List

from ev3dev.ev3 import Sound

from robot.movement.motor import MotorController, DEFAULT_SPEED, ROTATION_SPEED
from robot.movement.pid import PIDController
from robot.sensors.color import ColorSensor, Color, RGBColor
from robot.sensors.touch import TouchSensors
from utils.common import (
    Direction,
    PathStatus,
    direction_to_degrees,
    degrees_to_nearest_direction,
    flip_direction,
)


class MovementController:
    def __init__(self):
        self.motors = MotorController()
        self.pid_controller = PIDController()
        self.color_sensor = ColorSensor()
        self.touch_sensors = TouchSensors()
        self.sound = Sound()

        # to identify initialization
        self.__beep()
        self.__beep()

    def __beep(self):
        self.sound.beep()

    def __handle_turn_correction(self, correction):
        if abs(correction) != 0:
            left_speed = round(self.pid_controller.tp - correction)
            right_speed = round(self.pid_controller.tp + correction)
            self.motors.left.drive(left_speed)
            self.motors.right.drive(right_speed)
        else:
            self.motors.drive_both(DEFAULT_SPEED)

    def __handle_obstacle(self):
        self.motors.stop_both()
        self.__beep()
        self.motors.rotate_both(angle=(-70), speed=ROTATION_SPEED)
        self.motors.wait_while_running()
        self.motors.rotate_clockwise(angle=180, speed=ROTATION_SPEED)
        self.motors.wait_while_running()
        self.motors.reset_both()
        self.motors.drive_both(DEFAULT_SPEED)

    def travel_through_node(self):
        self.motors.rotate_both(angle=115, speed=ROTATION_SPEED)
        self.motors.wait_while_running()
        self.motors.stop_both()
        self.motors.reset_both()
        return self.color_sensor.get_rgb_color()

    def scan_for_paths(self, current_direction: Direction) -> Tuple[List[Direction], Direction]:
        current_direction_degrees = direction_to_degrees(current_direction)
        self.color_sensor.set_col_color_mode()
        # < --- scan for possible paths coming out of node --- >
        self.motors.reset_both()
        path_directions = set()
        self.motors.rotate_clockwise(angle=650, speed=ROTATION_SPEED)
        while self.motors.are_running():
            if self.color_sensor.get_color() == Color.BLACK:
                pos = self.motors.left.get_position()
                pos //= 2
                pos += current_direction_degrees
                d = degrees_to_nearest_direction(pos)
                path_directions.add(d)
        # < ------ >
        path_directions = list(path_directions)
        time.sleep(0.5)

        stop_direction = Direction.NORTH  # until proven otherwise
        # < --- keep going clockwise and stop at first black detection --- >
        if self.color_sensor.get_color() != Color.BLACK:
            self.motors.reset_both()
            self.motors.rotate_clockwise(angle=360, speed=ROTATION_SPEED)
            while self.motors.are_running():
                if self.color_sensor.get_color() == Color.BLACK:
                    self.motors.stop_both()
                    break
            pos = (self.motors.left.get_position() / 2) - 50
            degrees = current_direction_degrees + pos
            stop_direction = degrees_to_nearest_direction(degrees)
        # < ------ >
        time.sleep(0.5)
        self.color_sensor.set_rgb_raw_mode()

        self.__optmize_sensor_position_on_line()

        # print(
        #     f"raw scan path data: previous={current_direction}, directions={path_directions} new={stop_direction}"
        # )
        opposite_direction = flip_direction(current_direction)
        for d in path_directions:
            if d == opposite_direction:
                i = path_directions.index(d)
                del path_directions[i]
        print(
            f"after adjustments: previous={current_direction}, directions={path_directions} new={stop_direction}"
        )
        return path_directions, stop_direction

    def __optmize_sensor_position_on_line(self):
        self.motors.reset_both()
        self.motors.rotate_clockwise(angle=40, speed=(0.25 * ROTATION_SPEED))
        while self.motors.are_running():
            pos = self.motors.left.get_position()
            if pos > 14:
                self.motors.stop_both()
                return

    def rotate_to_chosen_direction(self, current_direction: Direction, new_direction: Direction):
        self.motors.reset_both()
        degrees = (360 - direction_to_degrees(current_direction)) + direction_to_degrees(
            new_direction
        )
        if degrees > 360:
            degrees -= 360
        n = (degrees // 45) - 1
        if n == 0:
            n = 1

        self.color_sensor.set_col_color_mode()
        self.motors.rotate_clockwise(angle=(n * 45), speed=ROTATION_SPEED)
        self.motors.wait_while_running()
        time.sleep(0.2)

        self.motors.reset_both()
        self.motors.rotate_clockwise(angle=55, speed=ROTATION_SPEED)
        while self.motors.are_running():
            if self.color_sensor.get_color() == Color.BLACK:
                self.motors.stop_both()
                break
        time.sleep(0.2)
        self.color_sensor.set_rgb_raw_mode()
        self.__optmize_sensor_position_on_line()

    def travel_vertex(self) -> Tuple[RGBColor, PathStatus, List[Tuple[int, int]]]:
        self.motors.reset_both()
        path_status = PathStatus.FREE  # until proven otherwise
        self.motors.append_to_positions_list(self.motors.get_both_motor_positions())
        self.motors.drive_both(DEFAULT_SPEED)
        while True:
            if self.color_sensor.get_rgb_color() != RGBColor.UNKNOWN:
                self.motors.stop_both()
                break

            if self.touch_sensors.are_pressed():
                self.__handle_obstacle()
                path_status = PathStatus.BLOCKED

            current_intensity = self.color_sensor.get_reflected_color_intensity()
            turn_correction = self.pid_controller.calculate_turn(current_intensity)
            self.__handle_turn_correction(turn_correction)
            self.motors.append_to_positions_list(self.motors.get_both_motor_positions())

        color = self.travel_through_node()
        positions_list = self.motors.get_positions_list()
        self.motors.clear_positions_list()
        self.pid_controller.reset_id_components()
        return color, path_status, positions_list

    @staticmethod
    def __degrees_to_direction(degrees: int) -> Direction:
        e = 45  # error margin
        compare_direction = lambda given, known: (known - e) < given < (known + e)
        if compare_direction(degrees, 90):
            return Direction.EAST
        elif compare_direction(degrees, 180):
            return Direction.SOUTH
        elif compare_direction(degrees, 270):
            return Direction.WEST
        elif compare_direction(degrees, 360):
            return Direction.NORTH
