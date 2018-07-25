#!/usr/bin/python

import ConfigParser
import subprocess
from time import localtime, strftime
import json
import paho.mqtt.client as mqtt

#
# Global variables
#
config = ConfigParser.ConfigParser()
config.read('/opt/mqtt-sensors-temp/conf')

responseTopic = 'sensors/temperature/'

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

#
# Callback that is executed when we disconnect from the broker.
#
def onDisconnect(client, userdata, message):
    print("Disconnected from the broker.")

#-----------------------------------------------------------------------------
# Main
#-----------------------------------------------------------------------------

# Call 1Wire for get temp
subprocess.call("/opt/mqtt-sensors-temp/w1-read-temp.sh")

# Create MQTT client instance
mqttc = mqtt.Client(client_id=config.get('MQTT', 'clientID'), clean_session=True)

mqttc.on_connect = onConnect
mqttc.on_disconnect = onDisconnect

# Connect to the broker
mqttc.username_pw_set(config.get('MQTT', 'user'), password=config.get('MQTT', 'passwd'))
mqttc.connect(config.get('MQTT', 'host'), port=int(config.get('MQTT', 'port')), keepalive=60, bind_address="")

mqttc.loop_start()

infoOutdoor = mqttc.publish((responseTopic + 'outdoor'), payload=getOutdoorTemp(), qos=0, retain=True)
infoOutdoor.wait_for_publish()

infoPool = mqttc.publish((responseTopic + 'sunlight'), payload=getPoolTemp(), qos=0, retain=True)
infoPool.wait_for_publish()

# End
