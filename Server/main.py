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
    mysqlQuery = MysqlQuery(HOST, DATABASE, USER, PASSWORD)
    mysqlQuery.connectDatabase()
    # mysqlQuery.deleteDataTable("device_1")

    mysqlQuery.insertTable("device_1", str(msg.payload))
    mysqlQuery.finishConnect()

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
    print("publish to cloudmqtt " + str(mid))


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


HOST = 'localhost'
DATABASE = 'MQTT_DATABASE'
USER = 'root'
PASSWORD = '123456'


client = mqtt.Client()
# Assign event callbacks
client.on_message = on_message
client.on_connect = on_connect
client.on_publish = on_publish
client.on_subscribe = on_subscribe

while True:
	# Set up password and IP
	client.username_pw_set("local_broker", "123456")
	client.connect('localhost', 1883)

	client.subscribe("srv/device_1/data", 0)
	client.loop_forever()


#Create object via contructor method __init__
# mysqlQuery = MysqlQuery(HOST, DATABASE, USER, PASSWORD)

"""Step to implement QUERY command to MySQL database
	1. Create MySQL database connection and cursor object to
		perform Database Operation
	2. Define MySQL queries such as INSERT, SELECT, DELETE
	3. Close database connection""" 

# mysqlQuery.connectDatabase()
# mysqlQuery.queryCmd("insert into device_1(DATA) values('test'")
# mysqlQuery.createTable("device_2")
# mysqlQuery.insertTable("mqtt_data", "hello world")
# mysqlQuery.deleteDataTable()
# mysqlQuery.readAllTable("mqtt_data")
# mysqlQuery.readRecentTable("device_1", 2)
# for i in range(2):
# 	mysqlQuery.createTable("device_" + str(i))
# mysqlQuery.finishConnect()
