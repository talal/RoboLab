from enum import IntEnum, unique
from typing import Tuple

import ev3dev.ev3 as ev3


@unique
class Color(IntEnum):
    NOCOLOR = 0
    BLACK = 1
    BLUE = 2
    GREEN = 3
    YELLOW = 4
    RED = 5
    WHITE = 6
    BROWN = 7


@unique
class RGBColor(IntEnum):
    UNKNOWN = -1
    BLUE = 0
    RED = 1


class ColorSensor:
    def __init__(self):
        self.sensor = ev3.ColorSensor(ev3.INPUT_2)
        self.sensor.mode = self.sensor.MODE_RGB_RAW
        self.blue: Tuple[int, int, int] = tuple()
        self.red: Tuple[int, int, int] = tuple()

    def calibrate_rgb(self):
        print("Press Left for blue calibration")
        print("Press Right for red calibration")
        print("Put on the starting line and press Down to complete calibration")
        b = ev3.Button()
        s = ev3.Sound()
        while True:
            if b.any():
                if b.left:
                    self.blue = self.get_rgb_raw()
                    s.beep()
                    print(f"BLUE calibrated as {self.blue}")
                elif b.right:
                    self.red = self.get_rgb_raw()
                    s.beep()
                    print(f"RED calibrated as {self.red}")
                elif b.down:
                    s.beep()
                    s.beep()
                    print(
                        f"color calibration complete: BLUE={self.blue} and RED={self.red}, will start intensity calibration shortly"
                    )
                    return

    def set_col_color_mode(self):
        self.sensor.mode = self.sensor.MODE_COL_COLOR

    def get_color(self) -> Color:
        if self.sensor.mode == self.sensor.MODE_COL_COLOR:
            return Color(self.sensor.value())
        else:
            raise Exception(
                f"expected sensor mode to be {self.sensor.MODE_COL_COLOR}, got {self.sensor.mode}"
            )

    def set_rgb_raw_mode(self):
        self.sensor.mode = self.sensor.MODE_RGB_RAW

    def get_rgb_raw(self) -> Tuple[int, int, int]:
        if self.sensor.mode == self.sensor.MODE_RGB_RAW:
            return self.sensor.bin_data("hhh")
        else:
            raise Exception(
                f"expected sensor mode to be {self.sensor.MODE_RGB_RAW}, got {self.sensor.mode}"
            )

    def get_reflected_color_intensity(self) -> int:
        if self.sensor.mode == self.sensor.MODE_RGB_RAW:
            return self.sensor.value()
        else:
            raise Exception(
                f"expected sensor mode to be {self.sensor.MODE_RGB_RAW}, got {self.sensor.mode}"
            )

    def get_rgb_color(self) -> RGBColor:
        e = 20  # error margin
        compare_rgb_values = lambda given, known: (
            (known[0] - e) < given[0] < (known[0] + e)
            and (known[1] - e) < given[1] < (known[1] + e)
            and (known[2] - e) < given[2] < (known[2] + e)
        )

        rgb_raw_value = self.get_rgb_raw()
        if compare_rgb_values(rgb_raw_value, self.blue):
            return RGBColor.BLUE
        elif compare_rgb_values(rgb_raw_value, self.red):
            return RGBColor.RED
        else:
            return RGBColor.UNKNOWN
