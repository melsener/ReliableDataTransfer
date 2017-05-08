import socket
import sys
import time
import select
from struct import *
from collections import namedtuple
import datetime
import math
import threading


UDP_PORT = [5004,5003,5002]
result=[] #packets will be stored here
HDR_FRMT='iHi988s' #format of packets
TIMEOUT=0 # as input argument

switchCount=0
IPList=[]
pkt = namedtuple("pkt", ["seq","chk_sum","flag","data"])
ack = namedtuple("pkt",["ackNo"])

def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

# Cite: http://stackoverflow.com/questions/1767910/checksum-udp-calculation-python
def checksum(msg):
    if (len(msg) % 2) != 0:
        msg += "0"

    s = 0
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8)
        s = carry_around_add(s, w)
	return ~s & 0xffff
		

def packetize(): # read from file and generate packets of 1000 bytes including sequence numbers, checksum ,end flag and data
	infile=open("inputc.txt","r")
	mesg=infile.read(988)
	count=0
	while mesg:
		result.append(pkt(seq=count,chk_sum = checksum(mesg),data=mesg,flag=1))
		mesg=infile.read(988)
		count+=1
	# put ending indicator flags for last packets
	if switchCount==1:
		result[-1]=pkt(seq=result[-1].seq,chk_sum=result[-1].chk_sum,data=result[-1].data,flag=0)
	elif switchCount==2:
		result[-1]=pkt(seq=result[-1].seq,chk_sum=result[-1].chk_sum,data=result[-1].data,flag=0)
		result[-2]=pkt(seq=result[-2].seq,chk_sum=result[-2].chk_sum,data=result[-2].data,flag=0)
	elif switchCount==3:
		result[-1]=pkt(seq=result[-1].seq,chk_sum=result[-1].chk_sum,data=result[-1].data,flag=0)
		result[-2]=pkt(seq=result[-2].seq,chk_sum=result[-2].chk_sum,data=result[-2].data,flag=0)
		result[-3]=pkt(seq=result[-3].seq,chk_sum=result[-3].chk_sum,data=result[-3].data,flag=0)
	infile.close()


def Send(ipID):
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	expected_ack=0
	unack=0
	sent=0
	index=ipID
	print "Thread Started no:" , ipID
	toperform=(len(result)/switchCount) + (len(result)%switchCount) #each thread will send its own sequence, packets are divided between threads
	while expected_ack < (toperform):
			mini=pack(HDR_FRMT,result[index].seq,result[index].chk_sum,result[index].flag,result[index].data) #turn into byte stream
			sock.sendto(mini, (IPList[ipID], UDP_PORT[ipID])) #send to corresponding IP address and port
			sent+=1
			ready = select.select([sock], [], [], TIMEOUT) #listen until timeout
			if ready[0]:#Packet received 
				pass
			else:	#Timeout
				continue
			raw_data, addr = sock.recvfrom(100)#get ACK from socket
			data=ack._make(unpack('I',raw_data))
			if data.ackNo==index:	#check if it is expected ACK
				expected_ack+=1
				index+=switchCount
			else:			# if not expected ACK, retransmit the last packet
				continue
	print "Thread Ended no:" , ipID
	sock.close()
	

threads=[]
if __name__ == "__main__":
	switchCount=int(sys.argv[1])
	# Get IP adresses as input
	for i in range(switchCount):
		ip=str(raw_input())
		IPList.append(ip)
	#Set timeout value
	print "Set timeout value:"
	TIMEOUT=float(raw_input())
	#create packets	
	packetize()
	# start transfer timer
	a=datetime.datetime.now()
	#create threads for sending
	for i in range(switchCount):
        	t = threading.Thread(target=Send, args=(i,))
        	threads.append(t)
        	t.start()
	#end threads
	for thread in threads:
    		thread.join()
	#stop transfer timer
	b=datetime.datetime.now()
	delta=b-a
	print "Elapsed time: ", int(delta.total_seconds()*1000)
	print "Transmission is Completed"	


	
