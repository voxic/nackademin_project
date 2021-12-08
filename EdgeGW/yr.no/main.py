#
# * Project: yr.no poller
# * File: main.py
# * Author: Emil Nildersen
# * Contact: emil@gr8c.se
#

## Imports
import sys
import time
import logging, traceback
import paho.mqtt.client as mqtt
import json
import requests


# Set this to the IP of your MQTT broker
mqtt_broker = "xxx.xxx.xxx.xxx"

# Device auth token
device_token = "xxxxx"

# Set MQTT topic.
topic = "v1/devices/me/telemetry"

# Set latitude for weather data
lat = "xxxx"
# Set longiude
lon = "xxxx"

# Yr.no API URL
url = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={}&lon={}".format(lat, lon)

# Yr.no headers, user-agent should point to where YR.no can contact you
headers = {
  'User-Agent': 'xxxxxx'
}

# Setup logger
logger = logging.getLogger() 
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(log_format)
logger.addHandler(handler)

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
            # Poll YR.no
            response = requests.request("GET", url, headers=headers, data={})

            yr_data = json.loads(response.text)
            temperature = yr_data['properties']['timeseries'][0]['data']['instant']['details']['air_temperature']
            wind = yr_data['properties']['timeseries'][0]['data']['instant']['details']['wind_speed']

            # Publish
            newPayload = {"ts" : ts, "values" : {"temperature" : str(temperature), "wind" : str(wind)}}
            mqttc.publish(topic, json.dumps(newPayload)) # Publish to broker
            logger.info("try to publish:{}".format(newPayload))

            # Set time between data points, 300 = 5 min
            time.sleep(300)

    except Exception as e:
        logger.error("exception main()")
        logger.error("e obj:{}".format(vars(e)))
        logger.error("message:{}".format(e.message))
        traceback.print_exc(file=sys.stdout)