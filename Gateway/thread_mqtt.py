import socket
import thread
import threading
import time
import sys
import random
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

def listen_and_publish(mess):
    global HOST
    global PORT
    global serv_sock
    global cli_addr
    print(mess)

    while True:
    	#receive data from multichannel process
        data, cli_addr = serv_sock.recvfrom(BUFFER)
        threadLock.acquire()
        json_obj = conv_to_json("device_1/data", 1, random.randint(0,100), random.randint(0,100), random.randint(0,100))
        mqttclient.publish("device_1/data", str(json_obj))
        threadLock.release()

def conv_to_json(topic, device_ID, temp, bright, humidity):
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


HOST = "localhost"
PORT = 10000
BUFFER = 1024
PORT_MQTT = 1883
# USERNAME_BROKER = "gateway"
# PASSWORD_BROKER = "raspberry"
USERNAME_BROKER = "local_broker"
PASSWORD_BROKER = "123456"


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
serv_sock.bind((HOST, PORT))
 
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
    thread.start_new_thread(listen_and_publish, ("create new thread",))
except:
    print("Error: unable to start thread")


# Synchronizing Thread
threadLock = threading.Lock()
mqttclient.subscribe("gw/device_1/req", 0)
# client.subscribe("test", 0)
mqttclient.loop_forever()
