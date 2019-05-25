import time 
import random
import json
from datetime import datetime
from firebase import firebase
from pyfcm import FCMNotification

try:
	import paho.mqtt.client as mqtt
except ImportError:

	import os
	import inspect
	cmd_subfolder = os.path.realpath(
		os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "../src")))
	if cmd_subfolder not in sys.path:
		sys.path.insert(0, cmd_subfolder)

	import paho.mqtt.client as mqtt
	print "import error"

#Define Call back MQTT
def on_connect(mosq, obj, rc):
	"""
	Connect MQTT Server
	:param mosq:
	:param obj:
	:param rc:
	:return:
	"""
	print ("on_connect:: Connected with result code " + str(rc))
	print("rc: " + str(rc))

def on_publish(mosq, obj, mid):
	"""
	Show message ID when publishing to MQTT Server
	:param mosq:
	:param obj:
	:param mid:
	:return:
	"""
	print("publish to mainserver " + str(mid))

def convert_data_to_json(topic, device_ID, time, temp, humidity, bright):
	"""
	Converse string data into json object
	"""
	data_input = {
		"topic" : topic,
		"device_ID" : device_ID,
		"cur_time" : time,
		"param" : {
				"sensor_temp" : temp,
				"sensor_bright" : bright,
				"sensor_humidity" : humidity
		}
	}
	#Convert from python dict to json object
	json_data = json.dumps(data_input, indent = 4)
	print(json_data)
	return json_data

#====================================================================
#							MAIN
#====================================================================
HOST = "localhost"
PORT_SOCKET = 10000
PORT_MQTT = 1883
USERNAME_BROKER = "local_broker"
PASSWORD_BROKER = "123456"

firebase = firebase.FirebaseApplication('https://lora-system-33293.firebaseio.com', None)
firebase.delete("", "")

mqttclient = mqtt.Client()
mqttclient.on_publish = on_publish
mqttclient.on_connect = on_connect

# Set up password and IP for MQTT client and connect to local broker runnning on raspbecd rry
mqttclient.username_pw_set(USERNAME_BROKER, PASSWORD_BROKER)
mqttclient.connect(HOST, PORT_MQTT)

while True:
	ID = random.randint(1,8)
	# ID = 1
	now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	temp = random.randint(0,100)
	humidity = random.randint(0,100)
	bright = random.randint(0,100)
	#Send data to database firebase
	firebase.post('End_device/deviceID_' + str(ID), {'time': now, 
											'temp': temp,
											'humidity': humidity, 
											'bright': bright})
	#Publish data to CloudMQTT
	json_obj = convert_data_to_json("device/data", ID, now, temp, humidity, bright)
	mqttclient.publish("device/data", str(json_obj))
	time.sleep(2)

