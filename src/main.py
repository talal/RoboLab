#!/usr/bin/env python3

import uuid

import paho.mqtt.client as mqtt

from robot.robot import Robot

client = None  # DO NOT EDIT


def run():
    # DO NOT CHANGE THESE VARIABLES
    #
    # The deploy-script uses the variable "client" to stop the mqtt-client after your program stops or crashes.
    # Your script isn't able to close the client after crashing.
    global client
    client = mqtt.Client(
        client_id=str(uuid.uuid4()),  # Unique Client-ID to recognize our program
        clean_session=False,  # We want to be remembered
        protocol=mqtt.MQTTv31,  # Define MQTT protocol version
    )

    # THE EXECUTION OF ALL CODE SHALL BE STARTED FROM WITHIN THIS FUNCTION.
    # ADD YOUR OWN IMPLEMENTATION HEREAFTER.

    r = Robot()
    r.get_ready(mqtt_client=client)
    r.start_exploration()


# DO NOT EDIT
if __name__ == "__main__":
    run()
