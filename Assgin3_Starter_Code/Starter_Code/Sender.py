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
pkt = packet.make_empty() #global packet for the 

# You can use some shared resources over the two threads
base = 0
mutex = _thread.allocate_lock()
timer = Timer(TIMEOUT_INTERVAL)

# Need to have two threads: one for sending and another for receiving ACKs

# Generate random payload of any length
def generate_payload(length=10):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str

# Send using Stop_n_wait protocol
def send_snw(sock, filename, lock):
	# Fill out the code here

    #open and read the file
    rBuf = open(filename, 'r')
    rBuf = rBuf.read()
    seq = 0
    while rBuf: #still data in the buff
        data = (rBuf[:PACKET_SIZE]).encode()#payload
        rBuf = rBuf[PACKET_SIZE:] #next part of the code
        #creation of the payload

        #sending the packet
        pkt = packet.make(seq, data)
        print("Sending seq# ", seq, "\n")
        udt.send(pkt, sock, RECEIVER_ADDR)
        #lock.acquire()
        #receive_snw(sock, pkt)
        seq = seq+1
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
def send_gbn(sock):

    return

# Receive thread for stop-n-wait
def receive_snw(sock, pkt, lock):
    # Fill here to handle acks
    pkt, sendrAdd = udt.recv(sock)
    ack, data = packet.extract(pkt)
    return

# Receive thread for GBN
def receive_gbn(sock):
    # Fill here to handle acks
    return


# Main function
if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     print('Expected filename as command line argument')
    #     exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SENDER_ADDR)

    filename = input('Enter the filename: ')
    
    print(mutex.locked())
    #_thread.start_new_thread(send_snw, (sock , filename, mutex))
    send_snw(sock, filename, mutex)
    print(mutex.locked())
    
    sock.close()


