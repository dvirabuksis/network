from struct import *
import select
import socket

#################################################
# all of the functions related to data transfer #
#          both for client and server           #
#################################################

def send_data(conn_soc, obj):
    """
    send data to client and make sure everything was sent
    """
    size = len(obj)
    sent_bytes = 0
    while sent_bytes < size:
        sent_bytes += conn_soc.send(obj[sent_bytes:])

def send_heaps_status(conn_soc,game):
    """
    send the status of the heaps as 3 integers to the client socket
    """
    obj = pack('iii',game.nA, game.nB, game.nC)
    send_data(conn_soc, obj)

def receive_char(client_soc):
    """
    attempt to receive a single char from the server
    """
    c = receive_data(client_soc, 1, 'c')[0]
    return c.decode('ascii')

def send_char(conn_soc, c):
    """
    send a value as single char to the client socket
    """
    send_data(conn_soc, pack('c',c.encode('ascii')))

def send_acceptance_status(conn_soc, status):
    """
    send message to the client if his game request was accepted or not
    """
    if status == "accept":
        send_char(conn_soc,'A')
    if status == "waitlist":
        send_char(conn_soc,'W')
    if status == "reject":
        send_char(conn_soc,'R')

def receive_acceptance_status(conn_soc):
    """
    send message to the client if his game request was accepted or not
    """
    status = "still connected"
    while status == "still connected":
        status = test_connection_and_if_read_ready(conn_soc)
    if status == "disconnected":
        print("Disconnected from server")
        conn_soc.close()
        exit(1)

    c = receive_char(conn_soc)
    if c == 'A':
        return "accept"
    if c == 'W':
        return "waitlist"
    if c == 'R':
        return "reject"

def wait_for_server(conn_soc):
    """
    wait for indication of starting game, after waiting in waitlist
    """
    return receive_acceptance_status(conn_soc)

def receive_data(conn_soc, size, format):
    """
    receive data from the client and make sure that everything arrived
    """
    data = conn_soc.recv(size)
    while len(data) < size:
        data += conn_soc.recv(size-len(data))
    return unpack(format, data)

def receive_turn(conn_soc):
    """
    attempt to receive a turn from the client, as a char and int
    possible values: first char [A,B,C,Q], second value [any integer]
    """
    (heap, num) = receive_data(conn_soc, 5, '>ci')
    heap = heap.decode('ascii')
    return [heap, num]

def receive_game_status(client_soc):
    """
    attempt to receive the game status from the server
    (as 3 integers that represent the heaps status)
    """
    (nA, nB, nC) = receive_data(client_soc, 12, 'iii')
    print("Heap A: {}\nHeap B: {}\nHeap C: {}".format(nA, nB, nC))

def test_connection_with_server(client_soc):
    """
    check if the connection with the server is still alive
    """
    try:
        readable, _, _ = select.select([client_soc],[],[],1)
        if len(readable) > 0:
            data = client_soc.recv(1024, socket.MSG_PEEK)
            if data == b'':
                return False
        return True
    except:
        return False

def test_connection_and_if_read_ready(client_soc):
    """
    check if the connection with the server is still alive
    """
    try:
        readable, _, _ = select.select([client_soc],[],[],1)
        if len(readable) > 0:
            data = client_soc.recv(1024, socket.MSG_PEEK)
            if data == b'':
                return "disconnected"
            return "got data"
        return "still connected"
    except Exception as err:
        return "disconnected"
