import sys
from typing import Tuple, Iterator

from ev3dev.ev3 import Sound

from planet.planet import Direction, PathStatus
from robot.movement.motor import MotorController, DEFAULT_SPEED, ROTATION_SPEED
from robot.movement.pid import PIDController
from robot.sensors.color import ColorSensor, Color, RGBColor
from robot.sensors.touch import TouchSensors


class MovementController:
    def __init__(self):
        self.motors = MotorController()
        self.pid_controller = PIDController()
        self.color_sensor = ColorSensor()
        self.touch_sensors = TouchSensors()
        self.sound = Sound()

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

    @staticmethod
    def __convert_angle_to_direction(angle):
        e = 40  # error margin
        compare_direction = lambda given, known: (known - 20) < given < (known + 20)
        if compare_direction(angle, 90):
            return Direction.EAST
        elif compare_direction(angle, 180):
            return Direction.SOUTH
        elif compare_direction(angle, 270):
            return Direction.WEST
        elif compare_direction(angle, 360):
            return Direction.NORTH
        else:
            return None

    def __handle_obstacle(self):
        self.motors.stop_both()
        self.__beep()
        self.motors.rotate_both(angle=(-50), speed=ROTATION_SPEED)
        self.motors.wait_while_running()
        self.motors.rotate_clockwise(angle=190, speed=ROTATION_SPEED)
        self.motors.wait_while_running()
        self.motors.reset_both()
        self.motors.drive_both(DEFAULT_SPEED)

    def travel_through_node(self):
        self.motors.rotate_both(angle=115, speed=ROTATION_SPEED)
        self.motors.wait_while_running()
        self.motors.stop_both()
        self.motors.reset_both()
        return self.color_sensor.get_rgb_color()

    def scan_for_paths(self) -> Iterator[Direction]:
        path_positions = set()
        self.color_sensor.set_col_color_mode()
        self.motors.rotate_clockwise(angle=360, speed=ROTATION_SPEED)
        while self.motors.are_running():
            if self.color_sensor.get_color() == Color.BLACK:
                path_positions.add(self.motors.left.get_position())
        self.color_sensor.set_rgb_raw_mode()

        path_angles = set([(p // 2) for p in path_positions])
        path_directions = filter(
            None, set([self.__convert_angle_to_direction(a) for a in path_angles])
        )

        # TODO: remove this
        print(path_positions)
        print(path_angles)
        print(path_directions)

        return path_directions

    def travel_vertex(self) -> Tuple[RGBColor, PathStatus]:
        path_status = PathStatus.FREE  # until proven otherwise
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

            # TODO: remove
            if self.touch_sensors.are_pressed():
                self.motors.stop_both()
                self.motors.reset_both()
                sys.exit(1)

        color = self.travel_through_node()
        self.pid_controller.reset_id_components()
        return color, path_status
