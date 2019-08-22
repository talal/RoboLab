from logger import get_logger
from robot.movement.movement import MovementController


logger = get_logger(__name__)

# this separator helps to distinguish the log entries for different runs
logger.debug("=" * 100)


class Robot:
    def __init__(self, mqtt_client):
        self.mqtt_client = mqtt_client
        self.movement_controller = None

    def get_ready(self):
        self.movement_controller = MovementController()
        self.movement_controller.pid_controller.calibrate(self.movement_controller.default_speed)

    def start_exploration(self):
        self.movement_controller.travel_vertex()
