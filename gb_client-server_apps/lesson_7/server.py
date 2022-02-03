import json
import logging
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from functions_server import check_request, ERR_PRESENCE_RESPONSE
from constants_server import ARGV, SIZE_OF_RECV, ADDR, PORT, \
    NEED_AUTHORIZATION, COUNT_OF_LISTENING
import logs.server_log_config

LOG = logging.getLogger('app.server')

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

try:
    # if 1024 > int(ARGV.port) > 65535:  # Включить для командной строки
    if 1024 > PORT > 65535:  # Выключить
        raise ValueError
    # server_socket.bind((ARGV.addr, int(ARGV.port))) # Включить для командной строки
    server_socket.bind((ADDR, PORT))  # Выключить
except ValueError:
    LOG.critical(
        f'Порт № {PORT} не подходит для подключения. Значение порта должно быть между 1024 и 65535')
server_socket.listen(COUNT_OF_LISTENING)

LOG.info(f'Запущен сервер с адресом: {ADDR}, порт {PORT}')

while True:
    client_socket, addr = server_socket.accept()
    req = json.loads(client_socket.recv(SIZE_OF_RECV).decode('utf-8'))
    LOG.info(
        f'От клиента {client_socket.getpeername()} поступило сообщение: {req}')
    try:
        if check_request(req) is None:
            raise ValueError
        else:
            if check_request(req) == 'close':
                LOG.info(
                    f"Клиент {client_socket.getpeername()} закрыл  соединение")
                client_socket.close()
            else:
                client_socket.send(check_request(req))
                LOG.info(
                    f"Клиенту {client_socket.getpeername()} отправлено сообщение {req}")
    except ValueError:
        LOG.critical(
            f'Функция {check_request.__name__} отметила сообщение от {client_socket.getpeername()} как некорректное!')
        client_socket.send(ERR_PRESENCE_RESPONSE.encode('utf-8'))
        LOG.info(f"Отправлено сообщение об ошибке: {ERR_PRESENCE_RESPONSE}")

# need_authorization?
