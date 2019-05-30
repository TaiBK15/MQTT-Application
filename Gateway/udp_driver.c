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

#define PORT    10000
#define MAXLINE 1024 

int sockfd = 0;
struct sockaddr_in servaddr;

/********************************************************************
udpStart()
/********************************************************************/
int udpStart() { 
    char *PORT_INFO = "REQ";


    // UDP SOCKET  
    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) { 
        perror("socket creation failed"); 
        return(EXIT_FAILURE); 
    }
  
    memset(&servaddr, 0, sizeof(servaddr)); 
    

    // SERVER INFORMATION 
    servaddr.sin_family = AF_INET; 
    servaddr.sin_port = htons(PORT); 
    servaddr.sin_addr.s_addr = INADDR_ANY; 


    /* INITIAL CONNECTION */
    /*HANDSHAKE: Client sends the first data as a initial signal to server to provide 
        address and opened port.*/
    // printf("UDP_DRIVER: Send initial signal\n");
    // sendto(sockfd, (const char *)PORT_INFO, strlen(PORT_INFO), MSG_CONFIRM, (const struct sockaddr *) &servaddr, sizeof(servaddr)); 
    // printf("UDP_DRIVER: Wait ACK from server\n");
    // sleep(3);


    // SUCCESS
    return sockfd; 
}
/********************************************************************
udpListen()
/********************************************************************/
int udpListen(char *udp_buffer) {
    int len = 0;
    len = recvfrom(sockfd, udp_buffer, MAXLINE, MSG_WAITALL, (struct sockaddr *) &servaddr, &len);
    if (len > 0)
        printf("UDP_DRIVER: UDP downlink message: %s\n", udp_buffer);

    return len;
}

/********************************************************************
udpSend()
/********************************************************************/
void udpSend(char *udp_buffer) {
    sendto(sockfd, udp_buffer, strlen(udp_buffer), MSG_CONFIRM, (const struct sockaddr *) &servaddr, sizeof(servaddr)); 
    printf("UDP_DRIVER: UDP uplink message: \n");
    puts(udp_buffer);
}
