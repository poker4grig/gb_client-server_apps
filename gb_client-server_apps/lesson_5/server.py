import argparse
import json
import logging
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from logs import server_log_config

from server_storage import PORT, ADDR, check_request, err_presence_response

LOG = logging.getLogger('app.server')

argv_parser = argparse.ArgumentParser(
    prog='command_line_server',
    description='аргументы командной строки сервера',
    epilog='автор - poker4grig'
)
argv_parser.add_argument('-a', '--addr', nargs='?', default=ADDR, help='help')
argv_parser.add_argument('-p', '--port', nargs='?', default=PORT, help='help')
argv = argv_parser.parse_args()

need_authorization = True

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

try:
    # if 1024 > int(argv.port) > 65535:  # Включить для командной строки
    if 1024 > PORT > 65535:  # Выключить
        raise ValueError
    # server_socket.bind((argv.addr, int(argv.port))) # Включить для командной строки
    server_socket.bind((ADDR, PORT))  # Выключить
except ValueError:
    LOG.critical(
        f'Порт № {PORT} не подходит для подключения. Значение порта должно быть между 1024 и 65535')
server_socket.listen(5)

LOG.info(f'Запущен сервер с адресом: {ADDR}, порт {PORT}')

while True:
    client_socket, addr = server_socket.accept()
    req = json.loads(client_socket.recv(4096).decode('utf-8'))
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
        client_socket.send(err_presence_response.encode('utf-8'))
        LOG.info(f"Отправлено сообщение об ошибке: {err_presence_response}")
# need_authorization?
