#!/usr/bin/python3 -u
"""
This module creates and runs an MQTT
client which runs arbitrary scripts
"""

import time
import os
import difflib
from subprocess import STDOUT, check_output
from paho.mqtt.client import Client

def connect(userdata, flags, return_code):
    """
    on_connect is called when the Client connects to the broker
    """
    print(userdata, flags)
    print("Connected with return code " + str(return_code))


class MQTTScriptClient(Client):
    """
    MQTTScriptClient extends the paho mqtt
    client to run arbitrary scripts
    """

    def __init__(self, auth, host, script_dir, topic_file):
        super().__init__()
        self.user = auth[0]
        self.connect_to_broker(auth, host)
        self.script_directory = script_dir
        self.topic_filename = topic_file
        self.scripts = self.get_scripts()
        self.topics = self.get_topics()

    def get_topics(self):
        """
        retrieve the topics the topic list file
        """
        return open(self.topic_filename).read().splitlines()

    def get_scripts(self):
        """
        retrieve the scripts from the script list file
        """
        return os.listdir(self.script_directory)

    def connect_to_broker(self, auth, host):
        """
        method used to connect to broker
        """
        self.username_pw_set(username=auth[0], password=auth[1])
        super().connect(host, port=1883, keepalive=60)

    def message_callback(self, userdata, msg):
        """
        on_message is called when a message is received from the broker
        This function also processes the message and executes the called
        script with the necessary arguments
        """
        print(userdata)
        payload = msg.payload.decode()
        print(msg.topic + " " + payload)

        # from empirical tests 0.3 seems to be a good threshold, one could use numbered
        # scripts or scripts with very different names and increase the threshold.
        script = difflib.get_close_matches(payload.split(" ")[0] + ".sh", self.scripts, 1, 0.3)
        print("script returned is: {}".format(script))
        command = ["scripts/{script}".format(script=script[0])]
        print("running script {}".format(script[0]))

        # if there's more than one keyword then either there are arguments
        # or there's a multi-word scripts, at the moment multi-word scripts cannot
        # be called correctly with arguments, thinking of a good fix.
        if len(payload.split(" ")) > 1:
            command.extend([" ".join(payload.split(" ")[1:])])
            print("the arguments are: {}".format(command[1:]))

        print("command is: {}".format(command))
        check_output(command, stderr=STDOUT, timeout=10)


    def subscribe_to_topics(self):
        """
        subscribing to all the topics in the topics file
        """
        for topic in self.topics:
            print(super().subscribe("{username}/f/{topic}".format(username=self.user, topic=topic)))

    def run_debug(self):
        """
        runs the client in debug mode, printing the topics and using loop_forever which
        blocks and is in general less flexible than self.loop_start
        """
        print(self.scripts)
        print(self.topics)
        self.subscribe_to_topics()
        self.loop_forever()

    def run(self):
        """
        runs the client in normal mode, currently unfinished
        """
        self.loop_start()
        time.sleep(1)
        self.subscribe_to_topics()
        while True:
            time.sleep(600)
            self.scripts = self.get_scripts()


def main():
    """
    main function which creates the MQTTScriptClient, overrides the methods of Client
    and starts the client.
    """
    authentication = open('auth').read().splitlines()
    client = MQTTScriptClient(authentication, 'io.adafruit.com', 'scripts', 'topics')
    client.on_connect = connect
    client.on_message = MQTTScriptClient.message_callback
    client.run_debug()

main()
