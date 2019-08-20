#!/usr/bin/env python3

# Suggestion: Do not import the ev3dev.ev3 module in this file
import json
import time

import paho.mqtt.client as mqtt

from planet import Direction


class Communication:
    global client

    def __init__(self, mqtt_client, map):
        """ Initializes communication module, connect to server, subscribe, etc. """
        # THESE TWO VARIABLES MUST NOT BE CHANGED
        self.client = mqtt_client

        # ADD YOUR VARIABLES HERE
        self.client = mqtt.Client(client_id="217", clean_session=False, protocol=mqtt.MQTTv31)
        self.client.username_pw_set('robot', password='H8zbos646n')  # Your group credentials
        self.client.connect('mothership.inf.tu-dresden.de', port=8883)
        self.client.on_message = self.on_message
        self.client.subscribe('explorer/217', qos=1)  # Subscribe to topic explorer/xxx

        self.recive = []  # list of recived unprocessed messages
        self.x = 0
        self.y = 0
        self.headingInv = "S"
        self.planet = ""
        self.target = 0
        self.tx = 0
        self.ty = 0
        self.map = map

    # THIS FUNCTIONS SIGNATURE MUST NOT BE CHANGED
    def on_message(self, client, data, message):
        message = json.loads(message.payload.decode('utf-8'))
        print("new message: ", message)
        if message["from"] == "server":
            self.recive.append(message)

    def landing(self):
        self.client.publish("explorer/217", '{"from": "client", "type": "ready"}', qos=1)
        self.client.loop_start()
        message = None
        while message is None:
            message = self.getMessage("planet")
        self.x = message["startX"]
        self.y = message["startY"]
        self.headingInv = "S"
        self.planet = "planet/" + message["planetName"] + "-217"
        print("channel: ", self.planet)
        self.client.subscribe(self.planet, qos=1)
        self.client.loop_stop()  # to finish the listning to the massege

    def getMessage(self, type):
        for message in self.recive:
            if message["type"] == type:
                this = message["payload"]  # get content of message
                self.recive.remove(message)  # delete message out of list
                return this
        return None

    def onPoint(self, sx, sy, sd, ex, ey, ed, state):
        self.client.loop_start()
        payload = {"startX": sx, "startY": sy, "startDirection": sd, "endX": ex, "endY": ey, "endDirection": ed,
                   "pathStatus": state}
        message = {"from": "client", "type": "path", "payload": payload}
        self.client.publish(self.planet, json.dumps(message), qos=1)
        time.sleep(2)  # wait 2 seconds for messages to come in
        messagge = None
        while message is None:
            message = self.getMessage("path")  # wait for the position
        print("got path correction:", message)
        self.x = message["endX"]  # update coordinates of the robotS
        self.y = message["endY"]
        self.headingInv = message["endDirection"]  # has to be inverted
        self.map.add_path(((message["startX"], message["startY"]), Direction(message["startDirection"])),
                          ((message["endX"], message["endY"]), Direction(message["startDirection"])),
                          message["pathWeight"])
        self.client.loop_stop()  # to finish the listning to the massege
        self.processMessages()

    def pathSelect(self, x, y, d):
        self.client.loop_start()
        payload = {"startX": x, "startY": y, "startDirection": d}
        message = {"from": "client", "type": "pathSelect", "payload": payload}
        self.client.publish(self.planet, json.dumps(message), qos=1)
        time.sleep(2)
        self.client.loop_stop()  # to finish the listning to the massege

        message = self.getMessage("pathSelect")
        if message is not None:  # wait for permission from server
            d = message["startDirection"]
        return d

    def processMessages(self):
        message = self.getMessage("pathUnveiled")
        while message is not None:
            print("process map:", message)
            self.map.add_path(((message["startX"], message["startY"]), Direction(message["startDirection"])),
                              ((message["endX"], message["endY"]), Direction(message["startDirection"])),
                              message["pathWeight"])
            message = self.getMessage("pathUnveiled")
        message = self.getMessage("target")
        if message is not None:
            print("process target:", message)
            self.tx = message["targetX"]
            self.ty = message["targetY"]
            self.target = 1
        message = self.getMessage("done")
        if message is not None:
            print("Done good Job\n", message["message"])

    def explorationCompleted(self):
        self.client.loop_start()
        payload = {"message": "finally!!!"}
        message = {"from": "client", "type": "explorationCompleted", "payload": payload}
        self.client.publish("explorer/217", json.dumps(message), qos=1)
        while not self.processMessages(): pass
        self.client.disconnect()
        print("explorationCompleted")

    def targetReached(self):
        self.client.loop_start()
        payload = {"message": "I'm here :)"}
        message = {"from": "client", "type": "targetReached", "payload": payload}
        self.client.publish("explorer/217", json.dumps(message), qos=1)
        while not self.processMessages(): pass
        self.client.disconnect()
        print("targetReached")
