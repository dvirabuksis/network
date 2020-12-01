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
    print("created a new client socket, running first round")
    send_acceptance_status(client,"accept")
    read_list.append(new_client)
    play_round(new_client,True)

def handle_new_client(client):
    """
    create a new game and add the client into playing clients list, if has space.
    if not, try adding to waitlist. if still no place then send rejection message.
    return true if the client had an available spot in 'playing client' (if started a game)
    """
    if (len(playing_clients) < max_num_of_players):
        initialize_game_for_client(client)
    elif (len(waitlist) < size_of_wait_list):
        print("client was added to waitlist")
        waitlist.append(client)
        send_acceptance_status(client,"waitlist")
    else:
        print("client was rejected")
        send_acceptance_status(client,"reject")
        
def pop_client_from_waitlist():
    """
    after a game is done, if there is a waiting client, start a game with him
    """
    if (len(waitlist) > 0):
        client = waitlist.pop(0)
        initialize_game_for_client(client)

def play_round(socket, is_first_round):
    """
    play a single round with a client. handle if the game is finished after it
    """
    is_over = run_single_round(socket,is_first_round)
    if(is_over):
        print("client game is over, deleting from lists")
        del playing_clients[socket]
        read_list.remove(socket)
        pop_client_from_waitlist()

#### run ####
try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('', server_port))
    server.listen(5)
    server.setblocking(0)

    read_list.append(server)

    while True:
        try:
            print("Server iteration, waiting for read ready sockets.")
            print("Current read list:",[socket.fileno() for socket in read_list])
            print("Current waitlist:",[socket.fileno() for socket in waitlist])
            readable, _, _ = select.select(read_list,[],[])
            for socket in readable:
                if socket is server:
                    print("readable socket: server")
                    new_client, _ = server.accept()
                    handle_new_client(new_client)
                else:
                    print("readable socket: client, running a single round")
                    play_round(socket,False)
            print("")
        except KeyboardInterrupt as error:
            print("Server was Stopped")
            break
        except OSError as error:
            if error.errno == errno.ECONNREFUSED:
                print("Failed to connect with client: connection refused by client")
            break
        except Exception as err:
            print("Server Error:",str(err))
            pass
    server.close()
except Exception as err:
    print("Error in creating server socket:",str(err))