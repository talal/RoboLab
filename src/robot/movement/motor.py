import ev3dev.ev3 as ev3


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

    def start(self):
        self.m.command = self.m.COMMAND_RUN_FOREVER

    def drive(self, speed):
        self.m.run_forever(speed_sp=speed)

    def rotate_to_angle(self, angle, speed):
        self.m.run_to_rel_pos(position_sp=angle, speed_sp=speed)

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
        self.left = Motor(ev3.OUTPUT_A)
        self.right = Motor(ev3.OUTPUT_D)

    def are_running(self):
        return self.left.is_running() or self.right.is_running()

    def wait_while_running(self):
        self.left.wait_while_running()
        self.right.wait_while_running()

    def start_both(self):
        self.left.start()
        self.right.start()

    def drive_both(self, speed):
        self.left.drive(speed)
        self.right.drive(speed)

    def rotate_clockwise(self, angle, speed):
        angle *= 2
        self.left.rotate_to_angle(angle, speed)
        self.right.rotate_to_angle(-angle, speed)
        self.wait_while_running()

    def rotate_counter_clockwise(self, angle, speed):
        angle *= 2
        self.left.rotate_to_angle(-angle, speed)
        self.right.rotate_to_angle(angle, speed)
        self.wait_while_running()

    def stop_both(self):
        self.left.stop()
        self.right.stop()

    def reset_both(self):
        self.left.reset()
        self.right.reset()
