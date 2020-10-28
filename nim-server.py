#!/usr/bin/python3
import socket
import errno
import sys
from struct import *

nA = int(sys.argv[1])
nB = int(sys.argv[2])
nC = int(sys.argv[3])
original_na = nA
original_nb = nB
original_nc = nC

if len(sys.argv) > 4:
    server_port = int(sys.argv[4])
else:
    server_port = 6444

def reset_heaps():
    global nA, nB, nC
    nA = original_na
    nB = original_nb
    nC = original_nc

def send_heaps_status(conn_soc):
    conn_soc.send(pack('iii',nA, nB, nC))

def send_char(conn_soc, c):
    conn_soc.send(pack('c',c.encode('ascii')))

def receive_turn(conn_soc):
    (heap, num) = unpack('cc',conn_soc.recv(2))
    heap = heap.decode('ascii')
    if heap == 'Q':
        num = 0
    else:    
        num = int(num.decode('ascii'))
    return [heap, num]

def apply_turn(heap, num):
    global nA, nB, nC
    if heap == "A":
        if num <= nA:
            nA -= num
        else:
            return False
    elif heap == "B":
        if num <= nB:
            nB -= num
        else:
            return False
    elif heap == "C":
        if num <= nC:
            nC -= num
        else:
            return False
    return True

def game_ended():
    return nA == 0 and nB == 0 and nC == 0

def server_move():
    global nA, nB, nC
    if nA < nB or nA < nC:
        if nB < nC:
            nC -= 1
        else:
            nB -= 1
    else:
        nA -= 1

def game(conn_soc):
    reset_heaps()
    winner = 0
    while True:
        send_heaps_status(conn_soc)
        if winner == 1:
            send_char(conn_soc,'W')
            break
        elif winner == 2:
            send_char(conn_soc, 'L')
            break
        else:
            send_char(conn_soc, 'T')
        
        heap, num = receive_turn(conn_soc)
        if (heap == 'Q'): break

        is_legal = apply_turn(heap, num)

        if not is_legal:
            send_char(conn_soc, 'I')
        else:
            send_char(conn_soc, 'A')
        
        if game_ended():
            winner = 1
        else:
            server_move()            
            if game_ended():
                winner = 2

    conn_soc.close()

try:
    soc_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc_obj.bind(('', server_port))
    soc_obj.listen(5)
    while True:
        (conn_soc, address) = soc_obj.accept()
        game(conn_soc)
    soc_obj.close()
except OSError as error:
    if error.errno == errno.ECONNREFUSED:
        print("Failed to connect with client: connection refused by client")
    else:
        print("Server Error:", error.strerror)
