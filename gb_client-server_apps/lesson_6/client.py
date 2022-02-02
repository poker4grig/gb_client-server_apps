import json
import logging
from socket import socket, AF_INET, SOCK_STREAM
from client_storage import presence_msg, send_message, PORT, ADDR, size_of_recv
import logs.client_log_config

LOG = logging.getLogger("app.client")

client_socket = socket(AF_INET, SOCK_STREAM)
# client_socket.connect((argv.addr, int(argv.port))) # Включить для ком.строки
client_socket.connect((ADDR, PORT))  # Выключить

LOG.debug(f'Передача шаблона сообщения: {presence_msg} для функции <<{send_message.__name__}>>')
client_socket.send(json.dumps(send_message(presence_msg)).encode('utf-8'))
LOG.debug(f'Функция <<{send_message.__name__}>> отправила на сервер сообщение: {presence_msg}')

while True:
    req = client_socket.recv(size_of_recv)
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
