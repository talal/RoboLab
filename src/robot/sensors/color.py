from enum import Enum, IntEnum, unique
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
class RGBColor(Enum):
    UNKNOWN = (0, 0, 0)
    BLUE = (53, 151, 146)
    RED = (197, 73, 42)


class ColorSensor:
    def __init__(self):
        self.sensor = ev3.ColorSensor(ev3.INPUT_2)
        self.sensor.mode = self.sensor.MODE_RGB_RAW

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
        for c in RGBColor:
            if compare_rgb_values(rgb_raw_value, c.value):
                return c
        return RGBColor.UNKNOWN
