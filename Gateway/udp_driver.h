#ifndef UDP_DRIVER_H
#define UDP_DRIVER_H
#include <stdio.h> 
#include <stdlib.h> 
#include <unistd.h> 

int udpStart();
int udpListen(char *udp_buffer);
void udpSend(char *udp_buffer);

#endif