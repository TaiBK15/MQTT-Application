import socket
import thread
import threading
import time
import sys
import json
import random

from Mysql_Driver import MysqlQuery

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

# Define event callbacks MQTT

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
	#send payload to C process using python
	serv_sock.sendto(msg.payload, cli_addr)



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


def on_log(mosq, obj, level, string):
	"""
	:param mosq:
	:param obj:
	:param level:
	:param string:
	:return:
	"""
	print(string)


def listen_and_publish():
	"""
	Multi channel RAK831 process
	Create the thread to listen via UDP socket
	"""
	global cli_addr
	# global serv_sock
	print("Create new thread")

	while True:
		#receive data from multichannel process
		data, cli_addr = serv_sock.recvfrom(BUFFER)
		threadLock.acquire()
		#Parse json data
		data_dict = json.loads(data_sample)
		save_to_database(str(data_dict['node_address']), str(data_dict['sensor_temp']), str(data_dict['sensor_humidity']), str(data_dict['sensor_lux']))
		json_obj = conv_to_json("device_" + str(data_dict['node_address']) + "/data", data_dict['node_address'], round(data_dict['sensor_temp']), round(data_dict['sensor_humidity']), round(data_dict['sensor_lux']))
		# json_obj = conv_to_json("device_1/data", 1, random.randint(0,100), random.randint(0,100), random.randint(0,100))
		mqttclient.publish("device_" + str(data_dict['node_address']) + "/data", str(json_obj))
		threadLock.release()

def conv_to_json(topic, device_ID, temp, humidity, bright):
	"""
	Converse string data into json object
	"""
	data_input = {
		"topic" : topic,
		"device_ID" : device_ID,
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


def save_to_database(device_ID, temp, humidity, bright):
	"""
	Access to database which created previously
	Save data into database 
	"""
	mysqlQuery = MysqlQuery(HOST, DATABASE, USERNAME_DB, PASSWORD_DB)
	mysqlQuery.connectDatabase()
	mysqlQuery.insertTable("device_" + device_ID, temp, humidity, bright)	

#
#-------------------MAIN----------------------
#

HOST = "localhost"
PORT_SOCKET = 10000
PORT_MQTT = 1883
USERNAME_BROKER = "gateway"
PASSWORD_BROKER = "raspberry"

DATABASE = "MQTT_DATA"
USERNAME_DB = "root"
PASSWORD_DB = "raspberry"
BUFFER = 1024

data_sample = """{
		"node_address" : 2,
		"sensor_humidity" : 60.7,
		"sensor_lux" : 25.7,
		"sensor_temp" : 30.3
}"""

mqttclient = mqtt.Client()
# Assign event callbacks
mqttclient.on_message = on_message
mqttclient.on_connect = on_connect
mqttclient.on_publish = on_publish
mqttclient.on_subscribe = on_subscribe

# Set up password and IP for MQTT client and connect to local broker runnning on raspberry
mqttclient.username_pw_set(USERNAME_BROKER, PASSWORD_BROKER)
mqttclient.connect(HOST, PORT_MQTT)

#Create socket UDP
serv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
serv_sock.bind((HOST, PORT_SOCKET))

#HANDSHAKE: Wait initial message 
while True:
	print("Wait initial mess from client\n")
	#receive data from multichannel process
	ini_mess, cli_addr = serv_sock.recvfrom(BUFFER)

	#Server sends ACK as soon as receiving message
	serv_sock.sendto("ACK from server", cli_addr)
	break

#Create thread for listen to RAK831 process
try:
	thread.start_new_thread(listen_and_publish, ())
except:
	print("Error: unable to start thread")

# Synchronizing Thread
threadLock = threading.Lock()
mqttclient.subscribe("device_1/req", 0)
mqttclient.subscribe("device_2/req", 0)
mqttclient.subscribe("device_3/req", 0)
mqttclient.subscribe("device_4/req", 0)
mqttclient.subscribe("device_5/req", 0)
mqttclient.subscribe("device_6/req", 0)
mqttclient.subscribe("device_7/req", 0)
mqttclient.subscribe("device_8/req", 0)
# client.subscribe("test", 0)
mqttclient.loop_forever()
