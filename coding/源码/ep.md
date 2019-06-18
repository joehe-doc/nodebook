```C++
#include <sys/epoll.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>

#define MAX_EVENTS 10
int initnetwork();

void setnonblocking(int sock)  
{  
    int opts;  
    opts=fcntl(sock,F_GETFL);  
    if(opts<0)  
    {  
        perror("fcntl(sock,GETFL)");  
        exit(1);  
    }  
    opts = opts|O_NONBLOCK;  
    if(fcntl(sock,F_SETFL,opts)<0)  
    {  
        perror("fcntl(sock,SETFL,opts)");  
        exit(1);  
    }     
}  
  
int main(int argc,char *agrv[])
{
	int epfd,listensk,clientsk,addrlen;
	int nRet = 0 ;
	struct epoll_event ev,events[MAX_EVENTS];
	struct sockaddr_in clientaddr;
	listensk= initnetwork();
	epfd=epoll_create(10);
	if(epfd == -1)
	{
		printf("epoll_create error!\n");	
	}
	ev.events=EPOLLIN;
	ev.data.fd=listensk;
	nRet =epoll_ctl(epfd,EPOLL_CTL_ADD,listensk,&ev);
	if(nRet == -1)
	{
		//strerror(errno);
		perror("epoll_ctl: fd ")	;
		exit(-1);
		//strerror(errno);
	}
	while(1)
	{
		nRet =epoll_wait(epfd,events,MAX_EVENTS,-1);
		if(nRet == -1)
		{
			printf("epoll_wait error!\n")	;		
			break;
		}
		for(int i = 0 ; i < nRet ; i++)
		{
			if(events[i].data.fd==listensk)
			{
				addrlen = sizeof(struct sockaddr);
				clientsk=accept(listensk,(struct sockaddr*)&clientaddr,&addrlen);
				setnonblocking(clientsk);	
				ev.events = EPOLLIN|EPOLLET;
				ev.data.fd = clientsk;
				epoll_ctl(epfd,EPOLL_CTL_ADD,clientsk,&ev);
				
			}
			else
			{
				char revbuff[1024]={0};
				char sendbuff[512]={0};
				int nRev =recv(events[i].data.fd,revbuff,1024,MSG_DONTWAIT);
				printf("Receive msg: %s. Length = %d . \n",revbuff,nRev);
				sprintf(sendbuff,"hello %d",events[i].data.fd);
				send(events[i].data.fd,sendbuff,strlen(sendbuff),0);
			}
		}
		
			
	}
	
return 0;	
}

int initnetwork()
{
	int listensk,clientsk;
	struct sockaddr_in svaddr;
	listensk=socket(AF_INET,SOCK_STREAM,0);
	memset(&svaddr, 0, sizeof(struct sockaddr_in));
	svaddr.sin_family = AF_INET;
	svaddr.sin_port = htons(27015);
	inet_aton("172.16.64.59",&svaddr.sin_addr);
	bind(listensk,(struct sockaddr*)&svaddr,sizeof(struct sockaddr));
	listen(listensk,5);	
	return listensk;
}

```