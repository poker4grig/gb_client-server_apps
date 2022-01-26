from socket import socket, AF_INET, SOCK_STREAM
import json
import time
# import argparse

# argv_parser = argparse.ArgumentParser(
#     prog='command_line_client',
#     description='аргументы командной строки клиента',
#     epilog='автор - poker4grig'
# )
# argv_parser.add_argument('-a', '--addr', nargs='?', default='', help='help')
# argv_parser.add_argument('-p', '--port', nargs='?', default=7777)
# argv = argv_parser.parse_args()

client_socket = socket(AF_INET, SOCK_STREAM)
# client_socket.connect((argv.addr, int(argv.port)))
client_socket.connect(('127.0.0.1', 7777))

presence_msg = {
    "action": "presence",
    "time": time.time(),
    "type": "status",
    "user": {
        "account_name": "poker4grig",
        "status": "In contact"
    }
}

auth_msg = {
    "action": "authenticate",
    "time": time.time(),
    "user": {
        "account_name": "poker4grig",
        "password": "1"
    }
}

client_socket.send(json.dumps(auth_msg).encode('utf-8'))
request = client_socket.recv(4096).decode('utf-8')
print(request)
client_socket.close()
