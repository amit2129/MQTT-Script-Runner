# MQTT-Script-Runner
python MQTT script runner  

This short script runs a python MQTT client which connects to io.adafruit.com and  
subscribes to a list of topics, for every new message it receives it checks which  
script has the closest name using difflab and runs it in a python subprocess.  

I use this script, and the integration between the google assistant,  
IFTTT and adafruit IO to run custom scripts by voice command on an Ubuntu machine.  


