#
# * Project: Weatherstation-simulation
# * File: main.py
# * Author: Emil Nildersen
# * Contact: emil@gr8c.se
#

## Imports
import sys
import time
import logging, traceback
import paho.mqtt.client as mqtt
import random
import json


# Set this to the IP of your MQTT broker
mqtt_broker = "10.0.0.81"

# Device auth token
device_token = "pldY8vPZl6SbFQTrSjXb"

# Set MQTT topic.
topic = "v1/devices/me/telemetry"

# Setup logger
logger = logging.getLogger() 
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(log_format)
logger.addHandler(handler)

# Set base values
last_temp = -14.0
last_wind = 0.10
last_rain = 0.00

if __name__ == '__main__':

    # Connect to Service domain MQTT
    try:
        mqttc = mqtt.Client()
        # Set username to device token
        mqttc.username_pw_set(username=device_token)
        logger.info("start connect")
        mqttc.connect(mqtt_broker, port=1883)
        logger.info("connect success")
        mqttc.loop_start()

        # Main Loop
        while True:
            ts = round(time.time()*1000)
            # Generate Temperature values
            new_temp = last_temp + (random.randint(-20, 20) / 100)
            new_temp = round(new_temp, 1)
            newPayload = {"ts" : ts, "values" : {"temperature" : str(new_temp)}}
            mqttc.publish(topic, json.dumps(newPayload)) # Publish to broker
            logger.info("try to publish:{}".format(newPayload))

            # Generate Wind values
            new_wind = last_wind + (random.randint(-20, 20) / 100)
            new_wind = round(new_wind, 2)
            if(new_wind < 0):
                new_wind = 0.00
            newPayload = {"ts" : ts, "values" : {"wind" : str(new_wind)}}
            mqttc.publish(topic, json.dumps(newPayload)) # Publish to broker
            logger.info("try to publish:{}".format(newPayload))

            # Generate Rain values, rain is only sent if it is over 1 mm
            new_rain = last_rain + (random.randint(-50, 50) / 100)
            new_rain = round(new_rain, 1)
            if(new_rain < 0):
                new_rain = 0.00
            if(new_rain > 1.0):
                newPayload = {"ts" : ts, "values" : {"rain": str(new_rain)}}
                mqttc.publish(topic, json.dumps(newPayload))
                logger.info("try to publish:{}".format(newPayload))            

            # Set new base value for next round
            last_temp = new_temp
            last_wind = new_wind
            last_rain = new_rain

            # Set time between data points
            time.sleep(300)

    except Exception as e:
        logger.error("exception main()")
        logger.error("e obj:{}".format(vars(e)))
        logger.error("message:{}".format(e.message))
        traceback.print_exc(file=sys.stdout)