from struct import *

def send_data(conn_soc, obj):
    """
    send data to client and make sure everything was sent
    """
    size = len(obj)
    sent_bytes = 0
    print(size)
    while sent_bytes < size:
        sent_bytes += conn_soc.send(obj[sent_bytes:])
    print(sent_bytes)

def send_heaps_status(conn_soc,game):
    """
    send the status of the heaps as 3 integers to the client socket
    """
    print(game.nA)
    print(game.nB)
    print(game.nC)
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