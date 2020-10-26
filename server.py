#!/usr/bin/python3
import socket

soc_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc_obj.bind((socket.gethostname(), 80))
soc_obj.listen(5)

while True:
    (conn_soc, address) = soc_obj.accept()
    print("Connection from {} has been established".format(address))
    conn_soc.send(bytes("Welcome to the server!", "utf-8"))


    conn_soc.close()

soc_obj.close()