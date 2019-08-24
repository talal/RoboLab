import ev3dev.ev3 as ev3


class TouchSensors:
    def __init__(self):
        self.left = ev3.TouchSensor(ev3.INPUT_1)
        self.right = ev3.TouchSensor(ev3.INPUT_4)

    def are_pressed(self):
        return self.left.value() or self.right.value()
