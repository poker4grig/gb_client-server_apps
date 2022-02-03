import json
import logging
from socket import socket, AF_INET, SOCK_STREAM
from functions_client import send_message
from constants_client import PRESENCE_MSG, PORT, ADDR, SIZE_OF_RECV, ARGV
import logs.client_log_config

LOG = logging.getLogger("app.client")

client_socket = socket(AF_INET, SOCK_STREAM)
# client_socket.connect((ARGV.addr, int(ARGV.port))) # Включить для ком.строки
client_socket.connect((ADDR, PORT))  # Выключить

LOG.debug(f'Передача шаблона сообщения: {PRESENCE_MSG} для функции <<{send_message.__name__}>>')
client_socket.send(json.dumps(send_message(PRESENCE_MSG)).encode('utf-8'))
LOG.debug(f'Функция <<{send_message.__name__}>> отправила на сервер сообщение: {PRESENCE_MSG}')

while True:
    req = client_socket.recv(SIZE_OF_RECV)
    if not req:
        break
    else:
        request = json.loads(req.decode('utf-8'))
        LOG.info(f'От сервера {client_socket.getpeername()} поступило сообщение: {request}')
        response = 'Some message!'
        client_socket.send(json.dumps(response).encode('utf-8'))
        LOG.info(f'На сервер отправлено сообщение: {response}')
LOG.info(f'Закрытие соединения')
client_socket.close()
