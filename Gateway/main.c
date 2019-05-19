#include <stdio.h> 
#include <stdlib.h> 
#include <unistd.h> 
#include <string.h> 
#include <sys/types.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <netinet/in.h> 
#include <stdbool.h>
#include "udp_driver.h"
#include "parson/parson.h"

#include <pthread.h>
#include <semaphore.h>

struct downlink_message_t {
	int device_id;
	bool switch_state;
};

struct uplink_message_t {
	int device_id;
	double sensor_humidity;
	double sensor_bright;
	double sensor_temp;
};

struct gateway_position_t {
	double gps_lat;
	double gps_long;
};


pthread_mutex_t mutex;  
char dwnlink_buff[1024];
char uplink_buff[1024];

void parseDownlinkMessage(struct downlink_message_t* downlink_message, char* downlink_buffer);
void serializeUplinkMessage(struct uplink_message_t* uplink_message, char* uplink_buffer);
void detectGatewayPosition(struct gateway_position_t* gateway_position);
void serializeGPSData(struct gateway_position_t* gateway_position, char* uplink_buffer);

void* listenDownlinkPacket() {
	printf("LISTEN DOWNLINK PACKET: Thread Creation\n");
	while(1) {
		// LISTEN DOWNLINK MESSAGE
		if ( udpListen(dwnlink_buff) > 0 ) { /* IF THERE IS DOWNLINK MESSAGE */
			pthread_mutex_lock(&mutex); /* LOCK OTHER THREAD */
			printf("LISTEN DOWNLINK PACKET: incoming downlink packet\n");
			
			// PARSE DOWNLINK MESSAGE
			struct downlink_message_t dwnlink_mess;
			printf("%s\n", dwnlink_buff);
			parseDownlinkMessage(&dwnlink_mess, dwnlink_buff); // PARSE DOWNLINL MESSAGE FROM dwnlink_buff TO dwnlink_mess
			printf("%d %d\n", dwnlink_mess.device_id, dwnlink_mess.switch_state);

			// SEND TO NODE
			// ...
			
			pthread_mutex_unlock(&mutex); /* UNLOCK OTHER THREAD */

			/* clear buffer */
			memset(dwnlink_buff, 0, sizeof(dwnlink_buff));
		}
	}
}

void* listenUplinkPacket() {
	printf("LISTEN UPLINK PACKET: Thread Creation\n");
	while(1) {
		// LISTEN UPLINK MESSAGE
		struct uplink_message_t uplnk_mess;
		uplnk_mess.device_id = 3;
		uplnk_mess.sensor_humidity = 60.7;
		uplnk_mess.sensor_bright = 25.7;
		uplnk_mess.sensor_temp = 30.3;

		// PROCESS PACKET INTO JSON
		memset(uplink_buff, 0, sizeof(uplink_buff));
		serializeUplinkMessage(&uplnk_mess, uplink_buff);	// serialize struct data uplnk_mess to json string uplink_buff
		
		// SEND TO PROCESS 2
		udpSend(uplink_buff);

		sleep(20);
	}
}

void* sendGPSToServer() {
	printf("SEND GPS TO SERVER: Thread Createion\n");
	while(1) {
		pthread_mutex_lock(&mutex); /* LOCK OTHER THREAD */
		struct gateway_position_t gw_pos;
		detectGatewayPosition(&gw_pos);
		memset(uplink_buff, 0, sizeof(uplink_buff));
		serializeGPSData(&gw_pos, uplink_buff);	// serialize struct data gw_pos to json string uplink_buff
		
		// SEND TO PROCESS 2
		udpSend(uplink_buff);

		pthread_mutex_unlock(&mutex); /* UNLOCK OTHER THREAD */

		sleep(10);
	}
}

int main() {

	udpStart();

	// THREAD CREATION
    int res;
    pthread_t thread_id;
    res = pthread_create(&thread_id, NULL, &listenDownlinkPacket, 0);	// thread listenDownlinkPacket
    if (res != 0) {  
        perror("THREAD_CREATION: Thread creation failed");
        exit(EXIT_FAILURE);
    }
	res = pthread_create(&thread_id, NULL, &listenUplinkPacket, 0);	// thread listenUplinkPacket
    if (res != 0) {  
        perror("THREAD_CREATION: Thread creation failed");
        exit(EXIT_FAILURE);
    }
	res = pthread_create(&thread_id, NULL, &sendGPSToServer, 0);	// thread sendGPSToServer
    if (res != 0) {  
        perror("THREAD_CREATION: Thread creation failed");
        exit(EXIT_FAILURE);
    }

    //Create mutex lock for synchronize multithread
    if( pthread_mutex_init(&mutex, NULL) !=0 ) {
        perror("MUTEX_CREATION: Mutex create error" );
        exit(-1);
    }

    while(1);

	return 0;

}


void parseDownlinkMessage(struct downlink_message_t* downlink_message, char* downlink_buffer) {

	// GET OBJECT FROM STRING
	JSON_Value *schema = json_parse_string(downlink_buffer);	// PARSE STRING TO JSON
	
	JSON_Object *_object = json_value_get_object(schema);	// CHANGE TYPE JSON_Value TO JSON_Object

	int deviceID = json_object_get_number(_object, "device_id");	// get value from key "deviceID"
	downlink_message->device_id = deviceID;
	int switch_state = json_object_get_boolean(_object, "switch_state");	// get value from key "switch"
	if (switch_state == 1) downlink_message->switch_state = true;
	else downlink_message->switch_state = false;
}

void serializeUplinkMessage(struct uplink_message_t* uplink_message, char* uplink_buffer) {
	
	JSON_Value *root_value = json_value_init_object();	// CREATE OBJECT
	JSON_Object *root_object = json_value_get_object(root_value);	// CHANGE VALUE TYPE TO OBJECT TYPE
	
	// put data to json data
	json_object_set_string(root_object, "type", "DATA");
	json_object_set_number(root_object, "device_id", uplink_message->device_id);
	json_object_set_number(root_object, "sensor_humidity", uplink_message->sensor_humidity);
	json_object_set_number(root_object, "sensor_bright", uplink_message->sensor_bright);
	json_object_set_number(root_object, "sensor_temp", uplink_message->sensor_temp);

	// put json data into string
	char *serialized_string = NULL;
	serialized_string = json_serialize_to_string_pretty(root_value);
	memcpy(uplink_buffer, serialized_string, strlen(serialized_string));

	// free memory
	json_value_free(root_value);
}

double count = 0;

void detectGatewayPosition(struct gateway_position_t* gateway_position) {
	// read gps for lat long

	// fake data
	gateway_position->gps_lat = 10.775901 + count;
	gateway_position->gps_long = 106.640535 + count;
	count = count + 0.004;


}

void serializeGPSData(struct gateway_position_t* gateway_position, char* uplink_buffer) {
	JSON_Value *root_value = json_value_init_object();	// CREATE OBJECT
	JSON_Object *root_object = json_value_get_object(root_value);	// CHANGE VALUE TYPE TO OBJECT TYPE

	// put data to json data
	json_object_set_string(root_object, "type", "GPS");
	json_object_set_number(root_object, "gps_lat", gateway_position->gps_lat);
	json_object_set_number(root_object, "gps_long", gateway_position->gps_long);

	// put json data into string
	char *serialized_string = NULL;
	serialized_string = json_serialize_to_string_pretty(root_value);
	memcpy(uplink_buffer, serialized_string, strlen(serialized_string));

	// free memory
	json_value_free(root_value);
}