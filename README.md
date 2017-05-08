# ReliableDataTransfer
Team Assignment for Computer Networking

This assignment expected us to implement a Reliable Data Transfer Protocol similar to RDT 3.0. As a team we decided to use Stop and Wait method with the help of ACK’s, sequence numbers, timers and checksum for reliable transfer. Since we had 3 topologies to work among we decided to use threads to increase program performance, speed and expolit multiple links at the same time.

For running Client code, as command line argument, give number of switches.
After starting the program, give destination IP adresses as input and set the timeout in seconds.
You can execute the code by:
```
python client.py <number_of_switches>
```
Input: IP adresses of destination and TIMEOUT value.

For running Server code, as command line argument, give number of switches and file size in Bytes.
You can execute the code by:
```
python server.py <number_of_switches> <file_size>
```
