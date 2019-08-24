import json
from enum import Enum, unique
from typing import Tuple

from paho.mqtt.client import connack_string

from planet.planet import Direction, PathStatus


@unique
class MessageType(Enum):
    ADJUST = "adjust"
    DONE = "done"
    ERROR = "error"
    EXPLORATION_COMPLETED = "explorationCompleted"
    NOTICE = "notice"
    PATH = "path"
    PATH_SELECT = "pathSelect"
    PATH_UNVEILED = "pathUnveiled"
    PLANET = "planet"
    READY = "ready"
    TARGET = "target"
    TARGET_REACHED = "targetReached"
    TESTPLANET = "testplanet"


class Communication:
    """
    Class to hold the MQTT client communication
    Feel free to add functions and update the constructor to satisfy your requirements and
    thereby solve the task according to the specifications
    """

    def __init__(self, mqtt_client, logger):
        """
        Initializes communication module, connect to server, subscribe, etc.
        :param mqtt_client: paho.mqtt.client.Client
        :param logger: logging.Logger
        """
        # DO NOT CHANGE THESE VARIABLES
        self.client = mqtt_client
        self.client.on_message = self.safe_on_message_handler
        self.client.on_connect = self.__on_connect
        self.logger = logger

        # Add your client setup here
        self.username = "217"
        self.password = "H8zbos646n"
        self.message_queue = list()
        self.explorer_topic = f"explorer/{self.username}"
        self.planet_name = ""
        self.planet_topic = ""

        self.client.username_pw_set(self.username, password=self.password)
        self.client.connect("mothership.inf.tu-dresden.de", 1883)
        self.subscribe_to_topic(self.explorer_topic)
        self.client.loop_start()

    #  ====================  Callbacks  ====================  #

    # DO NOT EDIT THE METHOD SIGNATURE
    def on_message(self, client, data, message):
        """
        Handles the callback if any message arrived
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        msg = json.loads(message.payload.decode("utf-8"))
        if msg["from"] != "client":
            self.message_queue.append(msg)
        self.logger.debug(json.dumps(msg, indent=2))

    # DO NOT EDIT THE METHOD SIGNATURE OR BODY
    #
    # This helper method encapsulated the original "on_message" method and handles
    # exceptions thrown by threads spawned by "paho-mqtt"
    def safe_on_message_handler(self, client, data, message):
        """
        Handle exceptions thrown by the paho library
        :param client: paho.mqtt.client.Client
        :param data: Object
        :param message: Object
        :return: void
        """
        try:
            self.on_message(client, data, message)
        except:
            import traceback

            traceback.print_exc()
            raise

    def __on_connect(self, client, data, flags, rc):
        if rc == 0:
            self.logger.debug("Succesfully connected to Mothership!")
        else:
            self.logger.debug(f"Could not connect to Mothership, got error: {connack_string(rc)}")

    #  ====================  Connection/Subscription  ====================  #

    def stop_loop_and_disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def subscribe_to_topic(self, topic):
        self.client.subscribe(topic, qos=1)
        self.logger.debug(f'Subscribed to "{topic}"')

    #  ====================  Message Publishing  ====================  #

    # DO NOT EDIT THE METHOD SIGNATURE
    #
    # In order to keep the logging working you must provide a topic string and
    # an already encoded JSON-Object as message.
    def send_message(self, topic, message):
        """
        Sends given message to specified channel
        :param topic: String
        :param message: Object
        :return: void
        """
        self.logger.debug(f"Send to {topic}")
        self.logger.debug(json.dumps(message, indent=2))

        if self.client and topic != "":
            self.client.publish(topic, payload=message, qos=1)
        else:
            raise Exception(f"Failed to publish the message, check logs")

    def send_ready_message(self):
        msg = {"from": "client", "type": MessageType.READY.value}
        return self.send_message(self.explorer_topic, json.dumps(msg))

    def send_testplanet_message(self, planet_name):
        msg = {
            "from": "client",
            "type": MessageType.TESTPLANET.value,
            "payload": {"planetName": planet_name},
        }
        return self.send_message(self.explorer_topic, json.dumps(msg))

    def send_path_message(
        self,
        start: Tuple[Tuple[int, int], Direction],
        end: Tuple[Tuple[int, int], Direction],
        status: PathStatus,
    ):
        msg = {
            "from": "client",
            "type": MessageType.PATH.value,
            "payload": {
                "startX": str(start[0][0]),
                "startY": str(start[0][1]),
                "startDirection": start[1].value,
                "endX": str(end[0][0]),
                "endY": str(end[0][1]),
                "endDirection": end[1].value,
                "pathStatus": status.value,
            },
        }
        return self.send_message(self.planet_topic, json.dumps(msg))

    def send_path_select_message(self, start: Tuple[Tuple[int, int], Direction]):
        msg = {
            "from": "client",
            "type": MessageType.PATH_SELECT.value,
            "payload": {
                "startX": str(start[0][0]),
                "startY": str(start[0][1]),
                "startDirection": start[1].value,
            },
        }
        return self.send_message(self.planet_topic, json.dumps(msg))

    def send_target_reached_message(self):
        msg = {
            "from": "client",
            "type": MessageType.TARGET_REACHED.value,
            "payload": {"message": "Reached target!"},
        }
        return self.send_message(self.explorer_topic, json.dumps(msg))

    def send_exploration_completed_message(self):
        msg = {
            "from": "client",
            "type": MessageType.EXPLORATION_COMPLETED.value,
            "payload": {"message": "Exploration complete!"},
        }
        return self.send_message(self.explorer_topic, json.dumps(msg))

    #  ====================  Message Handling  ====================  #

    def handle(self):
        msg = self.message_queue.pop(0)
        print(json.dumps(msg, indent=2))  # TODO: remove this before final push
        if msg["from"] == "debug":
            return

        msg_type = MessageType(msg["type"])
        payload = msg["payload"]

        if msg_type == MessageType.PLANET:
            name = payload["planetName"]
            self.planet_topic = f"planet/{name}/{self.username}"
            self.subscribe_to_topic(self.planet_topic)
            return msg_type, ((payload["startX"], payload["startY"]), Direction.NORTH)

        if msg_type == MessageType.TARGET:
            return msg_type, ((payload["targetX"], payload["targetY"]), None)

        if msg_type == MessageType.PATH_SELECT:
            return msg_type, Direction(payload["startDirection"])

        if (msg_type == MessageType.PATH) or (msg_type == MessageType.PATH_UNVEILED):
            return (
                msg_type,
                ((payload["startX"], payload["startY"]), Direction(payload["startDirection"])),
                ((payload["endX"], payload["endY"]), Direction(payload["endDirection"])),
                PathStatus(payload["pathStatus"]),
                payload["pathWeight"],
            )

        if msg_type == MessageType.DONE:
            return msg_type, payload["message"]
