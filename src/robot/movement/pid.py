class PIDController:
    """
    For reference:
        The PIDController is based on the following guide:
        http://www.inpharmix.com/jps/PID_Controller_For_Lego_Mindstorms_Robots.html
    """

    def __init__(self, offset, target_power, proportionality_constant):
        # TODO: consider tuning using the "Ziegler–Nichols Method"
        self.offset = offset
        self.tp = target_power
        self.kp = proportionality_constant
        # TODO: arbitrary values for ki and kd are used for now. Fine-tune with trial and error
        self.ki = 0.1 * proportionality_constant
        self.kd = 0.45 * proportionality_constant
        self.integral = 0
        self.last_error = 0

    def calculate_p_component(self, error):
        return self.kp * error

    def calculate_i_component(self, error):
        # integral tends to accumulate drastically and cause overshooting if
        # the robot loses the line for too long therefore we do some corrections
        opposite_signs = lambda x, y: ((x ^ y) < 0)
        if error == 0 or opposite_signs(error, self.last_error):
            self.integral = 0
        else:
            # TODO: try different dampening approaches to see which is best
            self.integral = ((2 / 3) * self.integral) + error
            # self.integral = (0.5 * self.integral) + error
            # self.integral = (0.1 * self.integral) + error

        # then use the updated integral to calculate turn component
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
        self.integral = 0
        self.last_error = 0
