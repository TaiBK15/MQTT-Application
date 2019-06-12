import time 
import random
import json
import thread
import threading
from datetime import datetime
from firebase import firebase

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

def on_subscribe(mosq, obj, mid, granted_qos):
	"""
	:param mosq:
	:param obj:
	:param mid:
	:param granted_qos:
	:return:
	"""
	print("This means broker has acknowledged my subscribe request")
	print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_message(mosq, obj, msg):
	"""
	Message from MQTT Server
	:param mosq:
	:param obj:
	:param msg:
	:return:
	"""
	global HOST
	global PORT
	print ("on_message:: this means  I got a message from broker for this topic")
	print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
	data_dict = json.loads(str(msg.payload))
	mqttclient.publish("device/sw_ack/id_" + str(data_dict["device_id"]), str(msg.payload), retain = True)


def convert_data_to_json(device_ID, time, temp, humidity, bright):
	"""
	Converse string data into json object
	"""
	data_input = {
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

def convert_ack_to_json(device_ID, sw_state):
	"""
	Converse string data into json object
	"""
	data_input = {
		"device_ID" : device_ID,
		"sw_state" : sw_state
	}
	#Convert from python dict to json object
	json_data = json.dumps(data_input, indent = 4)
	print(json_data)
	return json_data

def convert_gps_to_json(gps_lat, gps_long):
	"""
	Converse string data into json object
	"""
	data_input = {
		"topic" : "gw/gps",
		"gps" : {
				"gps_lat" : gps_lat,
				"gps_long" : gps_long
		}
	}
	#Convert from python dict to json object
	json_data = json.dumps(data_input, indent = 4)
	print(json_data)
	return json_data

def random_seq_online():
	"""
	Random connected device
	"""
	seq = ""
	num = random.randint(1,8)
	for i in range(num):
		seq = seq + str(random.randint(1,8))
	print(seq)
	return seq

def transport_message_to_cloud():
	for id in range (1,3):
		# # ID = random.randint(1,8)
		# sw_state = random.choice([True, False])
		# # # ID = 1
		# now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		# temp = random.randint(0,100)
		# humidity = random.randint(0,100)
		# bright = random.randint(0,100)
		# #Send data to database firebase
		# firebase.post('End_device/deviceID_' + str(id), {'time': now, 
		# 										'temp': temp,
		# 										'humidity': humidity, 
		# 										'bright': bright})
		# # Publish data to CloudMQTT
		# json_obj = convert_data_to_json(id, now, temp, humidity, bright)
		# mqttclient.publish("device/data", str(json_obj))

		#Publish gps to CloudMQTT
		gps_obj = convert_gps_to_json(10.760882 + 0.0001*random.randint(0,100),
									 106.661896 + 0.0001*random.randint(0,100))
		mqttclient.publish("gw/gps", str(gps_obj))
		time.sleep(3)
	for id in range (1,3):
		seq = random_seq_online()
		mqttclient.publish("device/online", seq, retain = True)
		# json_obj = convert_ack_to_json("device/sw_ack/id_" + str(ID), ID, sw_state)
		# mqttclient.publish("device/sw_ack/id_" + str(ID), str(json_obj), retain = True)
		time.sleep(3)
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
mqttclient.on_connect = on_connect
mqttclient.on_publish = on_publish
mqttclient.on_subscribe = on_subscribe
mqttclient.on_message = on_message

# Set up password and IP for MQTT client and connect to local broker runnning on raspbecd rry
mqttclient.username_pw_set(USERNAME_BROKER, PASSWORD_BROKER)
mqttclient.connect(HOST, PORT_MQTT)

#Create thread for listen to RAK831 process
try:
	thread.start_new_thread(transport_message_to_cloud, ())
except:
	print("Error: unable to start thread")

mqttclient.subscribe("device/req", 0)
mqttclient.loop_forever()





