import sys
from typing import Tuple

from ev3dev.ev3 import Sound

from robot.movement.motor import MotorController
from robot.movement.pid import PIDController
from robot.sensors.color import ColorSensor, RGBColor
from robot.sensors.touch import TouchSensors


class MovementController:
    default_speed = 200

    def __init__(self):
        self.motors = MotorController()
        self.pid_controller = PIDController()
        self.color_sensor = ColorSensor()
        self.touch_sensors = TouchSensors()
        self.sound = Sound()

    def __beep(self):
        self.sound.beep()

    def travel_through_node(self):
        self.motors.rotate_both(angle=135, speed=180)
        self.motors.wait_while_running()
        self.motors.stop_both()
        self.motors.reset_both()
        return self.color_sensor.get_rgb_color()

    def __handle_turn_correction(self, correction):
        if abs(correction) != 0:
            left_speed = round(self.pid_controller.tp - correction)
            right_speed = round(self.pid_controller.tp + correction)
            self.motors.left.drive(left_speed)
            self.motors.right.drive(right_speed)
        else:
            self.motors.drive_both(self.default_speed)

    def travel_vertex(self) -> Tuple[RGBColor, bool]:
        got_obstacle = False
        self.motors.drive_both(self.default_speed)
        while True:
            if self.color_sensor.get_rgb_color() != RGBColor.UNKNOWN:
                self.motors.stop_both()
                break

            # TODO: handle obstacle in path

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
        return color, got_obstacle
