import json
from enum import Enum, unique

from paho.mqtt.client import connack_string


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

        self.client.username_pw_set(self.username, password=self.password)
        self.client.connect("mothership.inf.tu-dresden.de", 1883)
        self.subscribe_to_topic(f"explorer/{self.username}")
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
        payload = json.loads(message.payload.decode("utf-8"))
        if payload["from"] == "server":
            self.message_queue.append(payload)
        self.logger.debug(json.dumps(payload, indent=2))

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
        self.logger.debug("Send to: " + topic)
        self.logger.debug(json.dumps(message, indent=2))

        # YOUR CODE FOLLOWS (remove pass, please!)
        pass
