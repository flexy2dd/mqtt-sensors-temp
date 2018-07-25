#!/usr/bin/python

import ConfigParser
from time import localtime, strftime
import json
import paho.mqtt.client as mqtt

#
# Global variables
#
config = ConfigParser.ConfigParser()
config.read('conf')

requestTopic  = 'sensors/temperature/+'        # Request comes in here. Note wildcard.
responseTopic = 'sensors/temperature/'        # Response goes here. Request ID will be appended later

def getPoolTemp():
    with open ('/var/1w_files/28-0000066e633b', "r") as poolFile:
        poolData = poolFile.read()

    return float(poolData[20:])/1000

def getOutdoorTemp():
    with open ('/var/1w_files/28-0000066f5a83', "r") as outdoorFile:
        outdoorData = outdoorFile.read()

    return float(outdoorData[20:])/1000

#
# Callback that is executed when the client receives a CONNACK response from the server.
#
def onConnect(client, userdata, flags, rc):
   print("Connected with result code " + str(rc))

   # Subscribe on request topic with a single-level wildcard.
   # Subscribing in on_connect() means that if we lose the connection and
   # reconnect then subscriptions will be renewed.
   client.subscribe(requestTopic, 0)    # topic, QoS

#
# Callback that is executed when a message is received.
#
def onMessage(client, userdata, message):
   requestTopic = message.topic

   requestID = requestTopic.split('/')[2]

   print("Received a time request on topic " + requestTopic + ".")

   if requestID=='outdoor':
       client.publish((responseTopic + requestID), payload=getPoolTemp(), qos=0, retain=False) # Publish the time to the response topic

   if requestID=='outdoor2':
       client.publish((responseTopic + requestID), payload=getOutdoorTemp(), qos=0, retain=False) # Publish the time to the response topic

#
# Callback that is executed when we disconnect from the broker.
#
def onDisconnect(client, userdata, message):
    print("Disconnected from the broker.")

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

# Create MQTT client instance
mqttc = mqtt.Client(client_id=config.get('MQTT', 'clientID'), clean_session=True)

mqttc.on_connect = onConnect
mqttc.on_message = onMessage
mqttc.on_disconnect = onDisconnect

# Connect to the broker
mqttc.username_pw_set(config.get('MQTT', 'user'), password=config.get('MQTT', 'passwd'))
mqttc.connect(config.get('MQTT', 'host'), port=int(config.get('MQTT', 'port', 1883)), keepalive=60, bind_address="")

# This is a blocking form of the network loop and will not return until the client
# calls disconnect(). It automatically handles reconnecting.
mqttc.loop_forever()

# End
