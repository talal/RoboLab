from typing import Tuple, List

import ev3dev.ev3 as ev3

DEFAULT_SPEED = 180
ROTATION_SPEED = int(0.9 * DEFAULT_SPEED)


class Motor:
    """
    Motor is the base class that provides basic methods for
    controlling a single motor.
    This class is never used on its own but rather serves as the base
    class for MotorController class.
    """

    def __init__(self, output_port):
        self.m = ev3.LargeMotor(output_port)
        self.m.stop_action = self.m.STOP_ACTION_BRAKE

    def is_running(self):
        return self.m.STATE_RUNNING in self.m.state

    def wait_while_running(self):
        self.m.wait_while(self.m.STATE_RUNNING)

    def drive(self, speed):
        self.m.run_forever(speed_sp=speed)

    def rotate_to_angle(self, angle, speed):
        self.m.run_to_rel_pos(position_sp=angle, speed_sp=speed)

    def get_position(self):
        return self.m.position

    def stop(self):
        self.m.stop()

    def reset(self):
        self.m.reset()


class MotorController:
    """
    MotorController class provides methods for controlling two motors, left and
    right, individually (throught the base class Motor) or as a single unit.
    """

    def __init__(self):
        self.left = Motor(ev3.OUTPUT_B)
        self.right = Motor(ev3.OUTPUT_D)
        self.positions: List[Tuple[int, int]] = list()

    def are_running(self):
        return self.left.is_running() or self.right.is_running()

    def wait_while_running(self):
        self.left.wait_while_running()
        self.right.wait_while_running()

    def drive_both(self, speed):
        self.left.drive(speed)
        self.right.drive(speed)

    def rotate_both(self, angle, speed):
        self.left.rotate_to_angle(angle, speed)
        self.right.rotate_to_angle(angle, speed)

    def rotate_clockwise(self, angle, speed):
        angle *= 2
        self.left.rotate_to_angle(angle, speed)
        self.right.rotate_to_angle(-angle, speed)

    def rotate_counter_clockwise(self, angle, speed):
        self.rotate_clockwise((-1 * angle), speed)

    def get_both_motor_positions(self) -> Tuple[int, int]:
        return self.left.get_position(), self.right.get_position()

    def append_to_positions_list(self, positions: Tuple[int, int]):
        self.positions.append(positions)

    def get_positions_list(self) -> List[Tuple[int, int]]:
        # return a copy so that a later list.clear() will not give us any surprises
        return self.positions.copy()

    def clear_positions_list(self):
        self.positions.clear()

    def stop_both(self):
        self.left.stop()
        self.right.stop()

    def reset_both(self):
        self.left.reset()
        self.right.reset()
