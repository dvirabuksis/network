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
    """
    reset the status of the heaps for every new game
    """
    global nA, nB, nC
    nA = original_na
    nB = original_nb
    nC = original_nc

def send_data(conn_soc, obj):
    """
    send data to client and make sure everything was sent
    """
    size = len(obj)
    sent_bytes = 0
    while sent_bytes < size:
        sent_bytes += conn_soc.send(obj[sent_bytes:])

def send_heaps_status(conn_soc):
    """
    send the status of the heaps as 3 integers to the client socket
    """
    send_data(conn_soc, pack('iii',nA, nB, nC))

def send_char(conn_soc, c):
    """
    send a value as single char to the client socket
    """
    send_data(conn_soc, pack('c',c.encode('ascii')))

def receive_turn(conn_soc):
    """
    attempt to receive a turn from the client, as a char and int
    possible values: first char [A,B,C,Q], second value [any integer]
    """
    (heap, num) = unpack('>ci', conn_soc.recv(5))
    heap = heap.decode('ascii')
    return [heap, num]

def apply_turn(heap, num):
    """
    apply a turn of the client on the heaps
    return a bool whether the turn was legal or not
    """
    if num <= 0: return False
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
    else:
        return False
    return True

def game_ended():
    """
    check if the game has ended (all heaps are empty), returns a bool
    """
    return nA == 0 and nB == 0 and nC == 0

def server_move():
    """
    apply a server move
    """
    global nA, nB, nC
    if nA < nB or nA < nC:
        if nB < nC:
            nC -= 1
        else:
            nB -= 1
    else:
        nA -= 1

def run_game(conn_soc):
    """
    run a single game between server and client, until someone wins,
    the client quits, or an error occures
    """
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
        try:
            print("waiting for socket")
            (conn_soc, address) = soc_obj.accept()
            print("got a socket starting game")
            run_game(conn_soc)
        except KeyboardInterrupt as error:
            print("ctrl c")
            break
        except Exception as err:
            print("error:",err)
            pass #client disconnected in the middle of communication, keep the server running 
    soc_obj.close()
except OSError as error:
    if error.errno == errno.ECONNREFUSED:
        print("Failed to connect with client: connection refused by client")
    else:
        print("Server Error:", error.strerror)
