# receiver.py - The receiver in the reliable data transer protocol
import packet
import socket
import sys
import udt

RECEIVER_ADDR = ('localhost', 8080)

# Receive packets from the sender w/ GBN protocol
def receive_gbn(sock):
  nxtSeq = 0 #will define the next expected sequence
  endStr = ''
  file = open('receiver_bio.txt', 'w')

  while endStr != 'END':
    pkt, senderaddr = udt.recv(sock) #receive the packet
    seq, data = packet.extract(pkt) #extract the contents
    data = data.decode()

    if nxtSeq == seq: #it is the correct pkt
      pkt = packet.make(nxtSeq, b'')
      file.write(data)
      nxtSeq += 1

    else: #if it is not the expected sequence number
      pkt = packet.make((nxtSeq - 1), b'')



# Receive packets from the sender w/ SR protocol
def receive_sr(sock, windowsize):
    # Fill here
  return


# Receive packets from the sender w/ Stop-n-wait protocol
def receive_snw(sock):
  endStr = ''
  inOrder = 0
  file = open('receiver_file_16.txt', 'w')

  while endStr!='END':
    pkt, senderaddr = udt.recv(sock)
    seq, data = packet.extract(pkt) #attain the seq
    data = data.decode()

    pkt = packet.make(seq, b'')
    udt.send(pkt, sock, senderaddr) #send ack
    if data != 'END':
      file.write(data)

    endStr = data
    print("From: ", senderaddr, ", Seq# ", seq, endStr)


# Main function
if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     print('Expected filename as command line argument')
    #     exit()

  sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  sock.bind(RECEIVER_ADDR)
    # filename = sys.argv[1]
  receive_gbn(sock)

    # Close the socket
  sock.close()