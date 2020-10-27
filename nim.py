#!/usr/bin/python3
import socket
import errno
import sys
from struct import *

def receive_game_status(client_soc):
    msg = client_soc.recv(12)
    (nA, nB, nC) = unpack('iii', msg)
    print("Heap A: {}\nHeap B: {}\nHeap C: {}".format(nA, nB, nC))

def receive_char(client_soc):
    msg = client_soc.recv(1)
    return unpack('c', msg)[0].decode('ascii')

def send_turn(client_soc, turn):
    if turn[0] == 'Q':
        client_soc.send(pack('cc', 'Q'.encode('ascii'), 'Q'.encode('ascii')))
        return False
    (heap, num) = turn
    client_soc.send(pack('cc', heap.encode('ascii'), num.encode('ascii')))
    return True

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
        receive_game_status(client_soc)

        move = receive_char(client_soc)
        if(move == 'W'):
            print("You Win!")
            break
        elif(move == "L"):
            print("Server win!")
            break
        print("Your turn:")

        turn = input().split(' ')
        if not send_turn(client_soc, turn): break # returns false if turn is Q 

        is_llegal = receive_char(client_soc)

        if is_llegal == "I":
            print("Illegal move")
        elif is_llegal == "A":
            print("Move accepted")

except OSError as error:
    if error.errno == errno.ECONNREFUSED:
        print("connection refused by server")
    else:
        print("Error", error.strerror)

client_soc.close()
print("Disconnected from server")
