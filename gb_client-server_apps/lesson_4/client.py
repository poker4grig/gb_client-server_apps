import argparse
import json
import time
from socket import socket, AF_INET, SOCK_STREAM

from client_storage import presence_msg, send_message

argv_parser = argparse.ArgumentParser(
    prog='command_line_client',
    description='аргументы командной строки клиента',
    epilog='автор - poker4grig'
)
argv_parser.add_argument('-a', '--addr', nargs='?', default='127.0.0.1',
                         help='help')
argv_parser.add_argument('-p', '--port', nargs='?', default=7777)
argv = argv_parser.parse_args()

client_socket = socket(AF_INET, SOCK_STREAM)
# client_socket.connect((argv.addr, int(argv.port))) # Включить для ком.строки
client_socket.connect(('127.0.0.1', 7777))  # Выключить

client_socket.send(json.dumps(send_message(presence_msg)).encode('utf-8'))

while True:
    req = client_socket.recv(4096)
    if not req:
        break
    else:
        request = json.loads(req.decode('utf-8'))
        print(request)
client_socket.close()
