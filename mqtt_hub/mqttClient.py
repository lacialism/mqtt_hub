### Declare all clients ###

import paho.mqtt.client as mqtt

# change this value #
ivuname=''          #
ivpw=''             #
#####################

subClient = mqtt.Client("subClient")
watchdogClient = mqtt.Client("watchdog")
DBClient = mqtt.Client("DB")