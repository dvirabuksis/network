#!/usr/bin/python3
import socket
import errno
import sys
from struct import *
from communication import *
from Game import *

nA = int(sys.argv[1])
nB = int(sys.argv[2])
nC = int(sys.argv[3])
max_num_of_players = int(sys.argv[4])
size_of_wait_list = int(sys.argv[5])
original_na = nA
original_nb = nB
original_nc = nC

if len(sys.argv) > 6:
    server_port = int(sys.argv[6])
else:
    server_port = 6444

def run_game(conn_soc):
    """
    run a single game between server and client, until someone wins,
    the client quits, or an error occures
    """
    game = Game(nA,nB,nC,conn_soc)
    winner = 0
    while True:
        send_heaps_status(conn_soc,game)
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

        is_legal = game.apply_client_turn(heap, num)

        if not is_legal:
            send_char(conn_soc, 'I')
        else:
            send_char(conn_soc, 'A')
        
        if game.is_done():
            winner = 1
        else:
            game.apply_server_turn()            
            if game.is_done():
                winner = 2

    conn_soc.close()

try:
    soc_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc_obj.bind(('', server_port))
    soc_obj.listen(5)
    while True:
        try:
            print("Waiting for a new connection")
            (conn_soc, address) = soc_obj.accept()
            print("Received a new connection, starting game")
            run_game(conn_soc)
        except KeyboardInterrupt as error:
            print("Server was Stopped")
            break
        except Exception as err:
            print("client disconnected with an error")
            pass #client disconnected in the middle of communication, keep the server running 
    soc_obj.close()
except OSError as error:
    if error.errno == errno.ECONNREFUSED:
        print("Failed to connect with client: connection refused by client")
    else:
        print("Server Error:", error.strerror)
