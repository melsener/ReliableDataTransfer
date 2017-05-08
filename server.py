import socket
from collections import namedtuple
from struct import *
import select
import sys
import threading

HDR_FRMT='iHi988s'

pkt = namedtuple("pkt", ["seq","chk_sum","flag","data"])
ack = namedtuple("pkt",["ackNo"])

UDP_IP = "0.0.0.0"
UDP_PORT = [5004,5003,5002]

TIMEOUT=0.01 #manipulate this

#expectedNo=0
switchCount=0	# as input argument
fileSize=0	# as input argument
def carry_around_add(a, b):
    #Helper function for checksum function
    c = a + b
    return (c & 0xffff) + (c >> 16)

# Cite: http://stackoverflow.com/questions/1767910/checksum-udp-calculation-python
def checksum(msg):
    #Compute and return a checksum of the given data
    
    if (len(msg) % 2) != 0:
        msg += "0"
    s = 0
    for i in range(0, len(msg), 2):
        w = ord(msg[i]) + (ord(msg[i+1]) << 8)
        s = carry_around_add(s, w)
        return ~s & 0xffff

def combine(): # Each thread writes its own file, after transmission combine them.
	txt=''
	if(fileSize%988!=0):
		packetCount=(fileSize/988) + 1
	else:
		packetCount=(fileSize/988)
	
	if switchCount==2:
		toread0=open("output0.txt","r")
		toread1=open("output1.txt","r")
		output=open("output.txt","w")
		for i in range(packetCount):
			if i%2==0:
				mesg=toread0.read(988)
				txt=txt+mesg
			elif i%2==1:
				mesg=toread1.read(988)
				txt=txt+mesg
		for i in range(fileSize):
			output.write(txt[i])
		output.close()
		return
				
	elif switchCount==3:
		toread0=open("output0.txt","r")
		toread1=open("output1.txt","r")
		toread2=open("output2.txt","r")
		output=open("output.txt","w")
		for i in range(packetCount):
			if i%3==0:
				mesg=toread0.read(988)
				txt=txt+mesg
			elif i%3==1:
				mesg=toread1.read(988)
				txt=txt+mesg
			elif i%3==2:
				mesg=toread2.read(988)
				txt=txt+mesg
		for i in range(fileSize):
			output.write(txt[i])
				
		output.close()
		return		

def receive(ipID):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((UDP_IP, UDP_PORT[ipID])) #each threads listens from any adress with different ports
        outfile=open("output"+str(ipID)+".txt","w")
        end=True
        expectedNo=ipID
        while end:
            ready = select.select([sock], [], [], TIMEOUT)
            if ready[0]:#Data received
		pass
            else: # Timeout
		pass
            raw_data, addr = sock.recvfrom(1000)	#listen continously
            data=pkt._make(unpack(HDR_FRMT,raw_data))	#Open packet for checking
            
            if checksum(data.data) != data.chk_sum:	#checksum control
	    	continue
	    
            if expectedNo!=data.seq:			#sequence number control
            	continue
            expectedNo+=switchCount
            if data.flag==0:	#End packet indicator
            	end=False
            raw_data=pack('I',data.seq) #I've got correct up to ackN
            outfile.write(data.data)
            sock.sendto(raw_data, addr) #should send ACK

       	print "Receiving is finished"
       	sock.close() #close socket
       	outfile.close()

threads=[]
if __name__ == "__main__":
	switchCount=int(sys.argv[1]) #for creating threads, get switchCount
	fileSize=int(sys.argv[2])    #for combining files get the file size
	for i in range(switchCount): #start threads for receiving
		t = threading.Thread(target=receive, args=(i,))
		threads.append(t)
		t.start()
	for thread in threads:	#stop threads
    		thread.join()
	combine() #combine different files after the transmission


