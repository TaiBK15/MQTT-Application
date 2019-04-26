#include <stdio.h> 
#include <stdlib.h> 
#include <unistd.h> 
#include <string.h> 
#include <sys/types.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <netinet/in.h> 
#include <stdbool.h>


#include <pthread.h>
#include <semaphore.h>
  
#define PORT     10000
#define MAXLINE 1024 

void *listenMQTTClient();

int sockfd, len, adrr_len, num_mess = 0;
char buffer[MAXLINE]; 
char *PORT_INFO = "REQ"; 
char *hello = "hello client send";
struct sockaddr_in servaddr;
bool serv_ack = false;
pthread_mutex_t mutex;   
  
int main() { 

    int res;
    pthread_t thread_id;

  
    // Creating socket file descriptor 
    if ( (sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0 ) { 
        perror("socket creation failed"); 
        exit(EXIT_FAILURE); 
    } 
  
    memset(&servaddr, 0, sizeof(servaddr)); 
    
    // Filling server information 
    servaddr.sin_family = AF_INET; 
    servaddr.sin_port = htons(PORT); 
    servaddr.sin_addr.s_addr = INADDR_ANY; 
   
    //Create thread to listen message from mqtt client process
    res = pthread_create(&thread_id, NULL, &listenMQTTClient, 0);
    if (res != 0){  
        perror("Thread creation failed");
        exit(EXIT_FAILURE);}

    //Create mutex lock for synchronize multithread
        if( pthread_mutex_init(&mutex, NULL) !=0 )
    {
        perror( "Mutex create error" );
        exit(-1);
    }

    /*HANDSHAKE: Client sends the first data as a initial signal to server to provide 
        address and opened port. Client will send continously until receiving ACK from server*/
    do{
        printf("send initial signal\n");
        sendto(sockfd, (const char *)PORT_INFO, strlen(hello), 
        MSG_CONFIRM, (const struct sockaddr *) &servaddr,  
            sizeof(servaddr)); 
        printf("wait ACK from server\n");
        sleep(3);
    }
    while(serv_ack == false);

    while(1)
    {
    num_mess++;
    sendto(sockfd, (const char *)hello, strlen(hello), 
        MSG_CONFIRM, (const struct sockaddr *) &servaddr,  
            sizeof(servaddr)); 
    printf("mess[%d] sent !\n", num_mess);
    sleep(5);
}
 return 0; 
} 

//Function to create thread listen message from mqtt client process
void *listenMQTTClient()
{
    printf("Create new thread\n");
    while(1){
    len = recvfrom(sockfd, (char *)buffer, MAXLINE,  
                MSG_WAITALL, (struct sockaddr *) &servaddr, 
                &len); 
    pthread_mutex_lock(&mutex);

    if(len){
        serv_ack = true;  //Stop handshake process
        buffer[len] = '\0'; 
        printf("%s\n", buffer);

    pthread_mutex_unlock(&mutex);
   }
}

}