import argparse
import json
import logging
from socket import socket, AF_INET, SOCK_STREAM
from client_storage import presence_msg, send_message, PORT, ADDR
import logs.client_log_config

LOG = logging.getLogger("app.client")

argv_parser = argparse.ArgumentParser(
    prog='command_line_client',
    description='аргументы командной строки клиента',
    epilog='автор - poker4grig'
)
argv_parser.add_argument('-a', '--addr', nargs='?', default=ADDR,
                         help='help')
argv_parser.add_argument('-p', '--port', nargs='?', default=PORT)
argv = argv_parser.parse_args()

client_socket = socket(AF_INET, SOCK_STREAM)
# client_socket.connect((argv.addr, int(argv.port))) # Включить для ком.строки
client_socket.connect((ADDR, PORT))  # Выключить
LOG.debug(f'Передача шаблона сообщения: {presence_msg} для функции <<{send_message.__name__}>>')
client_socket.send(json.dumps(send_message(presence_msg)).encode('utf-8'))
LOG.debug(f'Функция <<{send_message.__name__}>> отправила на сервер сообщение: {presence_msg}')

while True:
    req = client_socket.recv(4096)
    if not req:
        break
    else:
        request = json.loads(req.decode('utf-8'))
        LOG.info(f'От сервера {client_socket.getpeername()} поступило сообщение: {request}')
        response = 'Some message!'
        client_socket.send(json.dumps(response).encode('utf-8'))
        LOG.debug(f'На сервер отправлено сообщение: {response}')
client_socket.close()
