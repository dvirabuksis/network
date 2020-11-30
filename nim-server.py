#!/usr/bin/python3
import socket
import errno
import sys
import select
from struct import *
from communication import *
from Game import *

nA = int(sys.argv[1])
nB = int(sys.argv[2])
nC = int(sys.argv[3])
max_num_of_players = int(sys.argv[4])
size_of_wait_list = int(sys.argv[5])

if len(sys.argv) > 6:
    server_port = int(sys.argv[6])
else:
    server_port = 6444

playing_clients = {}

def run_single_round(socket, start):
    '''
    run a single round for a single game
    return true if the game is over, false if still going
    '''
    game = playing_clients[socket]
    # print("1")
    if(start == False):
        heap, num = receive_turn(socket)
        # print("1")
        if (heap == 'Q'): 
            return True
        # print("1")
        is_legal = game.apply_client_turn(heap, num)
        # print("1")
        if not is_legal:
            send_char(socket, 'I')
        else:
            send_char(socket, 'A')
        # print("1")
        game.apply_server_turn()
        # print("1")
    
    send_heaps_status(socket,game)
    
    if game.winner == 1:
        send_char(socket,'W')
        return True
    elif game.winner == 2:
        send_char(socket, 'L')
        return True
    else:
        send_char(socket, 'T')
    # print("1")
    
    return False

try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', server_port))
    server.listen(5)
    server.setblocking(0)

    read_list = [server]

    while True:
        try:
            print("run")
            readable, _, _ = select.select(read_list,[],[])
            for socket in readable:
                if socket is server:
                    print("server")
                    new_client, _ = server.accept()
                    # print("1")
                    read_list.append(new_client)
                    # print("2")
                    new_game = Game(nA,nB,nC)
                    # print("3")
                    playing_clients[new_client] = new_game
                    # print("4")
                    is_over = run_single_round(new_client,True)
                    # print("5")
                else:
                    print("client")
                    is_over = run_single_round(socket,False)
                    if(is_over):
                        del playing_clients[new_client]
        except KeyboardInterrupt as error:
            print("Server was Stopped")
            break
        except Exception as err:
            print("error")
            pass #client disconnected in the middle of communication, keep the server running 
    server.close()
except OSError as error:
    if error.errno == errno.ECONNREFUSED:
        print("Failed to connect with client: connection refused by client")
    else:
        print("Server Error:", error.strerror)
