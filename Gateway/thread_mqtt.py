import socket
import thread
import threading
import time
import sys
import json

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


# Define event callbacks

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
    print ("on_message:: this means  I got a message from broker for this topic")
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    # Send payload to C process
    # conn.sendall(msg.payload)


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

def listen_and_publish(mess):
 	global HOST
 	global PORT
 	BUFFER = 1024
 	print(mess)
 	#Create socket UDP
	serv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	serv_sock.bind((HOST, PORT))
	while True:
		#receive data from multichannel process
	    data, addr = serv_sock.recvfrom(BUFFER)
	    threadLock.acquire()
	    client.publish("local/test", str(data))
	    threadLock.release()


HOST = "localhost"
PORT = 10000
PORT_MQTT = 1883
USERNAME_BROKER = "gateway"
PASSWORD_BROKER = "raspberry"


client = mqtt.Client()
# Assign event callbacks
client.on_message = on_message
client.on_connect = on_connect
client.on_publish = on_publish
client.on_subscribe = on_subscribe

# Set up password and IP for MQTT client
client.username_pw_set(USERNAME_BROKER, PASSWORD_BROKER)
client.connect(HOST, PORT_MQTT)

#Create thread for listen to RAK831 process
try:
    thread.start_new_thread(listen_and_publish, ("create new thread",))
except:
    print("Error: unable to start thread")
# Synchronizing Thread
threadLock = threading.Lock()
client.subscribe("local/test", 0)
# client.subscribe("test", 0)
client.loop_forever()
