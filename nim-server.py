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
waitlist = []
read_list = []

def run_single_round(socket, is_first_round):
    '''
    run a single round for a single game
    return true if the game is over, false if still going
    '''
    game = playing_clients[socket]
    if(is_first_round == False):
        heap, num = receive_turn(socket)
        if (heap == 'Q'): 
            return True
        is_legal = game.apply_client_turn(heap, num)
        if not is_legal:
            send_char(socket, 'I')
        else:
            send_char(socket, 'A')
        game.apply_server_turn()
    
    send_heaps_status(socket,game)
    
    if game.winner == 1:
        send_char(socket,'W')
        return True
    elif game.winner == 2:
        send_char(socket, 'L')
        return True
    else:
        send_char(socket, 'T')
    
    return False

def initialize_game_for_client(client):
    """
    create a new game for a client and start it
    """
    new_game = Game(nA,nB,nC)
    playing_clients[client] = new_game
    send_acceptance_status(client,"accept")
    read_list.append(client)
    play_round(client,True)

def handle_new_client(client):
    """
    create a new game and add the client into playing clients list, if has space.
    if not, try adding to waitlist. if still no place then send rejection message.
    return true if the client had an available spot in 'playing client' (if started a game)
    """
    if (len(playing_clients) < max_num_of_players):
        initialize_game_for_client(client)
    elif (len(waitlist) < size_of_wait_list):
        waitlist.append(client)
        send_acceptance_status(client,"waitlist")
    else:
        send_acceptance_status(client,"reject")
        
def pop_client_from_waitlist():
    """
    after a game is done, if there is a waiting client, start a game with him
    """
    if (len(waitlist) > 0):
        client = waitlist.pop(0)
        initialize_game_for_client(client)

def remove_client(socket):
    del playing_clients[socket]
    read_list.remove(socket)
    pop_client_from_waitlist()

def play_round(socket, is_first_round):
    """
    play a single round with a client. handle if the game is finished after it
    """
    is_over = run_single_round(socket,is_first_round)
    if(is_over):
        remove_client(socket)

#### run ####
try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', server_port))
    server.listen(5)
    server.setblocking(0)

    read_list.append(server)

    while True:
        try:
            readable = []
            readable, _, _ = select.select(read_list,[],[])
            for conn_socket in readable:
                if conn_socket is server:
                    print("readable socket: server")
                    new_client, _ = server.accept()
                    print("got a new client with socket number:",new_client.fileno())
                    handle_new_client(new_client)
                else:
                    print("readable socket: client {}, running a single round".format(conn_socket.fileno()))
                    data = conn_socket.recv(1024, socket.MSG_PEEK)
                    if data == b'':
                        print("disconnected from client")
                        remove_client(conn_socket)
                        continue
                    play_round(conn_socket,False)
        except KeyboardInterrupt as error:
            print("Server was Stopped")
            break
        except OSError as error:
            if error.errno == errno.ECONNREFUSED:
                print("Failed to connect with client: connection refused by client")
            break
        except Exception as err:
            print("Server Error:",str(err))
            break
    server.close()
except Exception as err:
    print("Error in creating server socket:",str(err))