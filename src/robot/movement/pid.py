from logger import get_logger
from robot.movement.motor import MotorController, DEFAULT_SPEED, ROTATION_SPEED
from robot.sensors.color import ColorSensor


class PIDController:
    """
    For reference:
        The PIDController is based on the following guide:
        http://www.inpharmix.com/jps/PID_Controller_For_Lego_Mindstorms_Robots.html
    """

    def __init__(self):
        self.logger = get_logger(__name__)
        self.offset = 0
        self.tp = 0
        self.kp = 0
        self.ki = 0
        self.kd = 0
        self.integral = 0
        self.last_error = 0

    def calibrate(self):
        drive_speed = DEFAULT_SPEED
        mc = MotorController()
        cs = ColorSensor()
        color_intensity_list = list()

        def rotate_and_append_light_intensity(rotate_func):
            rotate_func(angle=30, speed=ROTATION_SPEED)
            while mc.are_running():
                color_intensity_list.append(cs.get_reflected_color_intensity())
            rotate_func(angle=(-1 * 30), speed=ROTATION_SPEED)  # go back to the starting position
            mc.wait_while_running()

        rotate_and_append_light_intensity(mc.rotate_clockwise)
        rotate_and_append_light_intensity(mc.rotate_counter_clockwise)

        min_intensity = min(color_intensity_list)
        max_intensity = max(color_intensity_list)
        critical_gain = (drive_speed - (-1 * drive_speed)) / (max_intensity - min_intensity)

        self.offset = int(((max_intensity + min_intensity) * 0.5))
        self.tp = drive_speed
        self.kp = 0.16 * critical_gain
        self.ki = 0.14 * critical_gain
        self.kd = 0.3 * critical_gain

        self.logger.debug(
            f"PID controller: calibrating using color intensity values={color_intensity_list}, min={min_intensity}, max={max_intensity}"
        )
        self.logger.debug(
            f"PID controller: constants are offset={self.offset}, tp={self.tp}, kp={self.kp}, ki={self.ki}, kd={self.kd}"
        )

    def calculate_p_component(self, error):
        return self.kp * error

    def calculate_i_component(self, error):
        # integral tends to accumulate drastically and causes overshooting if the
        # robot loses the line for too long therefore we do a pre-update correction
        values_have_opposite_signs = lambda x, y: ((x ^ y) < 0)
        if (-5 < error < 5) or values_have_opposite_signs(error, self.last_error):
            self.integral = 0
            return 0
        else:
            self.integral = ((2 / 3) * self.integral) + error

        # use the updated integral to calculate turn component
        return self.ki * self.integral

    def calculate_d_component(self, error):
        derivative = error - self.last_error  # change in error
        return self.kd * derivative

    def calculate_turn(self, light_intensity):
        if not light_intensity:
            return 0

        error = light_intensity - self.offset
        p = self.calculate_p_component(error)
        i = self.calculate_i_component(error)
        d = self.calculate_d_component(error)

        self.last_error = error  # this MUST be at the end, just before return
        return round((p + i + d), 3)

    def reset_id_components(self):
        self.integral = 0
        self.last_error = 0
        self.logger.debug("PID controller: integral and last error values have been reset")
