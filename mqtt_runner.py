#!/usr/bin/python3 -u

import time
import os
import difflib
from paho.mqtt.client import Client
from subprocess import call



class MQTTScriptClient(Client):
    def __init__(self, auth, host, script_dir, topic_file):
        super().__init__()
        self.user = auth[0]
        self.connect(auth, host)
        self.script_directory = script_dir
        self.topic_filename = topic_file
        self.scripts = self.get_scripts()
        self.topics = self.get_topics()

    def get_topics(self):
        return open(self.topic_filename).read().splitlines()

    def get_scripts(self):
        return os.listdir(self.script_directory)

    def connect(self, auth, host):
        self.username_pw_set(username=auth[0], password=auth[1])
        super().connect(host, port=1883, keepalive=60)

    # FOR-DEBUG printing the rc on connection.
    def on_connect(self, userdata, flags, rc):
        print("Connected with return code " + str(rc))

    # printing message and running script
    def on_message(self, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
        script = difflib.get_close_matches(str(msg.payload), self.scripts, 1, 0.3)
        command = "scripts/{script}".format(script=script[0])
        print("running script {}".format(script[0]))
        call(command)

    # subscribing to all the topics in the topics file
    def subscribe(self):
        for topic in self.topics:
            print(super().subscribe("{username}/f/{topic}".format(username=self.user, topic=topic)))

    def run_debug(self):
        print(self.scripts)
        print(self.topics)
        self.subscribe()
        self.loop_forever()

    def run(self):
        self.loop_start()
        time.sleep(1)
        self.subscribe()
        while True:
            time.sleep(600)
            self.scripts = self.get_scripts()

def main():
    authentication = open('auth').read().splitlines()
    client = MQTTScriptClient(authentication, 'io.adafruit.com', 'scripts', 'topics')
    client.on_connect = MQTTScriptClient.on_connect
    client.on_message = MQTTScriptClient.on_message
    client.run_debug()

main()

