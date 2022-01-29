import json
import time
from socket import socket, AF_INET, SOCK_STREAM
from client_storage import presence_msg, send_message, argv, size_of_recv


client_socket = socket(AF_INET, SOCK_STREAM)
# client_socket.connect((argv.addr, int(argv.port))) # Включить для ком.строки
client_socket.connect(('127.0.0.1', 7777))  # Выключить

client_socket.send(json.dumps(send_message(presence_msg)).encode('utf-8'))

while True:
    req = client_socket.recv(size_of_recv)
    if not req:
        break
    else:
        request = json.loads(req.decode('utf-8'))
        print(request)
client_socket.close()
