from logger import get_logger
from robot.movement.motor import MotorController
from robot.sensors.color import ColorSensor

logger = get_logger(__name__)


class PIDController:
    """
    For reference:
        The PIDController is based on the following guide:
        http://www.inpharmix.com/jps/PID_Controller_For_Lego_Mindstorms_Robots.html
    """

    def __init__(self):
        self.offset = 0
        self.tp = 0
        self.kp = 0
        self.ki = 0
        self.kd = 0
        self.integral = 0
        self.last_error = 0

    def calibrate(self, drive_speed):
        mc = MotorController()
        cs = ColorSensor()
        color_intensity_list = list()

        # rotate to 40 degrees using the given rotate_func at increments of 5 degrees
        # while appending the light intensity to the collective list
        def rotate_and_append(rotate_func):
            for i in range(0, 40, 5):  # get light intensity
                color_intensity_list.append(cs.get_reflected_color_intensity())
                rotate_func(angle=5, speed=180)
            rotate_func(angle=(-1 * 40), speed=180)  # go back to the starting position

        rotate_and_append(mc.rotate_clockwise)
        rotate_and_append(mc.rotate_counter_clockwise)

        min_intensity = min(color_intensity_list)
        max_intensity = max(color_intensity_list)
        # proportionality constant, i.e (change in y-axis)/(change in x-axis)
        # where y-axis = motor power and x-axis = color intensity
        proportionality_constant = (drive_speed - (-1 * drive_speed)) / (
            max_intensity - min_intensity
        )
        proportionality_constant *= 0.65

        # TODO: do test runs on the big planet and fine-tune if needed
        self.offset = int((max_intensity - min_intensity) / 2)
        self.tp = drive_speed  # target power at which both motors run when error = 0
        self.kp = round(proportionality_constant, 3)
        self.ki = round((0.1 * proportionality_constant), 3)
        self.kd = round((0.44 * proportionality_constant), 3)

        logger.debug(
            f"calibrating PID controller using color intensity values = {color_intensity_list}"
        )
        logger.debug(
            f"PID controller constants are offset={self.offset}, tp={self.tp}, kp={self.kp}, ki={self.ki}, kd={self.kd}"
        )

    def calculate_p_component(self, error):
        return self.kp * error

    def calculate_i_component(self, error):
        # integral tends to accumulate drastically and causes overshooting if the
        # robot loses the line for too long therefore we do a pre-update correction
        values_have_opposite_signs = lambda x, y: ((x ^ y) < 0)
        if error == 0 or values_have_opposite_signs(error, self.last_error):
            self.integral = 0
        else:
            # TODO: integral dampening is not finalized, it might require fine-tuning
            self.integral = (0.1 * self.integral) + error

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
        return p + i + d

    def reset(self):
        self.offset = 0
        self.tp = 0
        self.kp = 0
        self.ki = 0
        self.kd = 0
        self.integral = 0
        self.last_error = 0
        logger.debug("PID controller has been reset")
