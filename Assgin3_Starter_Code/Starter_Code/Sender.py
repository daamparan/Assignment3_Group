import socket
import sys
import _thread
import time
import string
import packet
import udt
import random
from timer import Timer

# Some already defined parameters
PACKET_SIZE = 512
RECEIVER_ADDR = ('localhost', 8080)
SENDER_ADDR = ('localhost', 9090)
SLEEP_INTERVAL = 0.05 # (In seconds)
TIMEOUT_INTERVAL = 0.5
WINDOW_SIZE = 4

# You can use some shared resources over the two threads
base = 0
mutex = _thread.allocate_lock()
timer = Timer(TIMEOUT_INTERVAL)
total_Num = 0
total_Re = 0

done = False #used for ack

# Need to have two threads: one for sending and another for receiving ACKs
def set_window_size(num_packets):
    global base
    return min(WINDOW_SIZE, num_packets - base)

# Generate random payload of any length
def generate_payload(length=10):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str

# Send using Stop_n_wait protocol
def send_snw(sock, filename):
	# Fill out the code here

    #open and read the file
    rBuf = open(filename, 'r')
    rBuf = rBuf.read()
    seq = 0

    global total_Num
    global total_Re

    while rBuf: #still data in the buff

        data = (rBuf[:PACKET_SIZE]).encode()#payload
        rBuf = rBuf[PACKET_SIZE:] #next part of the read data
        #creation of the payload

        #sending the packet
        pkt = packet.make(seq, data)
        print("Sending seq# ", seq, "\n")
        udt.send(pkt, sock, RECEIVER_ADDR)

        _thread.start_new_thread(receive_snw, (sock, pkt)) #wait portion of protocol
        while not done:
        	continue

        #continuation
        #done = False
        seq = seq+1
        total_Num = total_Num + 1
        time.sleep(TIMEOUT_INTERVAL)
    pkt = packet.make(seq, "END".encode())
    udt.send(pkt, sock, RECEIVER_ADDR)
    
    '''
    seq = 0
    while(seq < 20):
        data = generate_payload(40).encode()
        pkt = packet.make(seq, data)
        print("Sending seq# ", seq, "\n")
        udt.send(pkt, sock, RECEIVER_ADDR)
        seq = seq+1
        time.sleep(TIMEOUT_INTERVAL)
    pkt = packet.make(seq, "END".encode())
    udt.send(pkt, sock, RECEIVER_ADDR)
    '''

# Send using GBN protocol
def send_gbn(sock, filename):
    global mutex
    global total_Num
    global total_Re
    global base
    global done
    global WINDOW_SIZE

    #open and read the file
    file = open(filename, 'r')
    seq = 0
    packets = [] #first collect the packets

    while 1:
        data = file.read(PACKET_SIZE)
        if not data: #if no data exists
            #packets.append(packet.make(seq, 'END'.encode())) #end packet
            break
        packets.append(packet.make(seq, data.encode())) #add to the packets
        seq = seq + 1


    nextSend = 0 #next seq to be sent
    base = 0 #base packet

    _thread.start_new_thread(receive_gbn, (sock,)) #start the receiving thread

    while base < len(packets): #while there is still more packets
        mutex.acquire() #lock the previous thread
        
        while nextSend < base + WINDOW_SIZE: #while we are within the window
            if nextSend <= len(packets):
                udt.send(packets[nextSend], sock, RECEIVER_ADDR) #send the packet at position 1
                nextSend = nextSend + 1
                total_Num = total_Num + 1
        
        if not timer.running(): #check whether the timer is running 
            timer.start()

        while not timer.timeout(): #if we are still running and not timed out
            mutex.release() #release the lock
            time.sleep(SLEEP_INTERVAL) #sleep for x time
            mutex.acquire() #attain the lock once again 

        else:
            timer.stop()
            nextSend = base #attain the last packet sent to send it again
            total_Re = total_Re + 1
        '''
        if done: #we acknowledged
            base = base + 1
            done = False #rst
        '''
        base += 1
       
        mutex.release() #release the thread


# Receive thread for stop-n-wait
def receive_snw(sock, pkt):
	t = Timer(TIMEOUT_INTERVAL) #timer during the timeout
	t.start()
	seq = (packet.extract(pkt))[0] #seq of the pkt that was sent
	global done
	global total_Num
	global total_Re

	while not done:
		r = udt.recv(sock) #try to receive the pkt tuple
		ack = packet.extract(r[0]) #extract only packet not the data 
		ack = ack[0] #attain the seq number by itseld 

		if ack == seq: #check if its the same pacakge
			print('Packet confirmed: Moving on')
			timer.stop()
			done = True
			break 

		if t.timeout: #if the timer timed out
			udt.send(pkt, sock, RECEIVER_ADDR) #send again
			t.stop() #stop the timer
			t.start()#start a new timer
		total_Num = total_Num + 1
		total_Re = total_Re + 1



# Receive thread for GBN
def receive_gbn(sock):
    global mutex
    global base
    global timer
    global total_Re
    global total_Num
    global done
    
    while True: #continously receive packets
        pkt, senderAddr = udt.recv(sock)
        ack, data = packet.extract(pkt)
        if (ack >= base):
            mutex.acquire()
            base = ack + 1 #this is the next seq that comes after it
            done = True
            timer.stop()
            mutex.release()


# Main function
if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     print('Expected filename as command line argument')
    #     exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SENDER_ADDR)

    filename = input('Enter the filename: ')
    t = time.time()
    #_thread.start_new_thread(send_snw, (sock, filename))
    send_gbn(sock, filename)
    print('Time Taken: ', time.time() - t)
    print('Total Packets sent', total_Num)
    print('Total Re-Sent Packets', total_Num)
    sock.close()


