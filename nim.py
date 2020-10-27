#!/usr/bin/python3
import socket
import errno
import sys
from struct import *

try:
    client_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_port = 6444
    client_host = 'localhost'

    if len(sys.argv) > 1:
        client_host = sys.argv[1]
        if len(sys.argv)>2:
            client_port = int(sys.argv[2])
    
    client_soc.connect((client_host, client_port))
    while True:
        msg = client_soc.recv(12)
        (nA, nB, nC) = unpack('iii', msg)
        print("Heap A: {}\nHeap B: {}\nHeap C: {}".format(nA, nB, nC))

        msg = client_soc.recv(1)
        (move) = unpack('c', msg)
        move = move[0].decode('ascii')

        if(move == 'W'):
            print("You Win!")
            break
        elif(move == "L"):
            print("Server win!")
            break
        print("Your turn:")

        turn = input().split(' ')
        if turn[0] == 'Q':
            client_soc.send(pack('cc', 'Q'.encode('ascii'), 'Q'.encode('ascii')))
            break

        (heap, num) = turn
        client_soc.send(pack('cc', heap.encode('ascii'), num.encode('ascii')))

        is_llegal =unpack('c', client_soc.recv(1)) 
        is_llegal = is_llegal[0].decode('ascii')

        if is_llegal == "I":
            print("Illegal move")
        elif is_llegal == "A":
            print("Move accepted")

except OSError as error:
    if error.errno == errno.ECONNREFUSED:
        print("connection refused by server")
    else:
        print(error.strerror)

print("Disconnected from server")
client_soc.close()
