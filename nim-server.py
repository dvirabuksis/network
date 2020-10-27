#!/usr/bin/python3
import socket
import errno
import sys
from struct import *

nA = int(sys.argv[1])
nB = int(sys.argv[2])
nC = int(sys.argv[3])
if len(sys.argv) > 4:
    server_port = int(sys.argv[4])
else:
    server_port = 6444

try:
    soc_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc_obj.bind(('', server_port))
    soc_obj.listen(5)
    while True:
        (conn_soc, address) = soc_obj.accept()
        winner = 0

        while True:
            conn_soc.send(pack('iii',nA, nB, nC))
            if winner == 1:
                conn_soc.send(pack('c','W'.encode('ascii')))
                break
            elif winner == 2:
                conn_soc.send(pack('c','L'.encode('ascii')))
                break
            else:
                conn_soc.send(pack('!c','T'.encode('ascii')))
            
            (heap, num) =unpack('cc',conn_soc.recv(2))

            if heap.decode('ascii') == 'Q':
                break
            
            num = int(num.decode('ascii'))
            heap = heap.decode('ascii')
            error = False
            if heap == "A":
                if num <= nA:
                    nA -= num
                else:
                    error = True
            elif heap == "B":
                if num <= nB:
                    nB -= num
                else:
                    error = True
            elif heap == "C":
                if num <= nC:
                    nC -= num
                else:
                    error = True
            elif heap == "Q":
                break
            else:
                error = True

            if error:
                conn_soc.send(pack('c','I'.encode('ascii')))
            else:
                conn_soc.send(pack('c','A'.encode('ascii')))
                if nA == 0 and nB == 0 and nC == 0:
                    winner = 1

            if nA != 0 or nB != 0 or nC != 0:
                if nA < nB or nA < nC:
                    if nB < nC:
                        nC -= 1
                    else:
                        nB -= 1
                else:
                    nA -= 1
                
                if nA == 0 and nB == 0 and nC == 0:
                    winner = 2

        conn_soc.close()
    soc_obj.close()
except OSError as error:
    if error.errno == errno.ECONNREFUSED:
        print("connection refused by server")
    else:
        print(error.strerror)
