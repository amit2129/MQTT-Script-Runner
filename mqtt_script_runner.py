#!/usr/bin/python3
import paho.mqtt.client as mqtt
import os
from subprocess import call
import difflib

# can be any path to a directory
# with script you may want to run
# os.listdir returns a list of names

topics = open('topics').read().splitlines()
print("topics are: {}".format(topics))

scripts = os.listdir('scripts')
print("scripts are: {}".format(scripts))

auth = open('auth').read().splitlines()
user = auth[0]
passwd = auth[1]

mqtt_service = 'io.adafruit.com'


# FOR-DEBUG printing the rc on connection.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))


# printing message and running script
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    script = difflib.get_close_matches(str(msg.payload), scripts,1, 0.3)[0]
    command = "scripts/{script}".format(script=script)
    print("command is {}".format(command))
    call(command)


# subscribing to all the topics in the topics file
def subscribe(client):
    for topic in topics:
        client.subscribe("{username}/f/{topic}".format(username=user, topic=topic))


# binding subscribe method to mqtt.Client
# so I can use can call it as a class method
mqtt.Client.subscribe_topics = subscribe

client = mqtt.Client()
client.on_connect=on_connect
client.on_message = on_message
client.username_pw_set(username=user,password=passwd)
client.connect(mqtt_service)
client.subscribe_topics()
client.loop_forever()
