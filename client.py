#!/usr/bin/python3
import socket
import errno


client_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_soc.connect((socket.gethostname(), 80))
msg = client_soc.recv(1024)
print(msg.decode("utf-8"))

# except OSError as error:
#     if error.errno == errno.ECONNREFUSED:
#         print("connection refused by server")
#     else:
#         print(error.strerror)

client_soc.close()