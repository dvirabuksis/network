#!/usr/bin/python3
import socket
import errno
import sys
from struct import *

game_ended_without_error = True

def receive_game_status(client_soc):
    """
    attempt to receive the game status from the server
    (as 3 integers that represent the heaps status)
    """
    msg = client_soc.recv(12)
    (nA, nB, nC) = unpack('iii', msg)
    print("Heap A: {}\nHeap B: {}\nHeap C: {}".format(nA, nB, nC))

def receive_char(client_soc):
    """
    attempt to receive a single char from the server
    """
    msg = client_soc.recv(1)
    return unpack('c', msg)[0].decode('ascii')

def send_turn(client_soc, turn):
    """
    send a turn to server
    if the turn is quit(Q) returns False
    else, returns True
    """
    if turn[0] == 'Q':
        client_soc.send(pack('>ci', 'Q'.encode('ascii'), 0))
        return False
    
    # for every illegal move that is in an incorrect format (char,int) we send a genric
    # illegal move - ('I',0)
    if (len(turn) != 2):
        heap = 'I'
        num = 0
    else:
        (heap, num) = turn
        try:
            num = int(num)
        except:
            heap = 'I'
            num = 0
        if len(heap) != 1:
            heap = 'I'
            num = 0
    client_soc.send(pack('>ci', heap.encode('ascii'), num))
    return True

try:
    client_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = 6444
    hostname = 'localhost'

    if len(sys.argv) > 1:
        hostname = sys.argv[1]
        if len(sys.argv)>2:
            port = int(sys.argv[2])
    
    print("setting up a connection:",hostname,":",port)
    client_soc.connect((hostname, port))

    while True:
        receive_game_status(client_soc)

        move = receive_char(client_soc)
        if(move == 'W'):
            print("You Win!")
            break
        elif(move == "L"):
            print("Server win!")
            break
        print("Your turn:") # move = 'T'

        turn = input().split(' ')
        if not send_turn(client_soc, turn): break # send_turn returns false if turn is Q

        is_llegal = receive_char(client_soc)

        if is_llegal == "I":
            print("Illegal move")
        elif is_llegal == "A":
            print("Move accepted")

except OSError as error:
    game_ended_without_error = False
    if error.errno == errno.ECONNREFUSED:
        print("Failed to connect to server: connection refused by server")
    else:
        print("Disconnected from server")
        print("Error:", error.strerror)

client_soc.close()
if (game_ended_without_error): print("Disconnected from server")
