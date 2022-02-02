import json
import logging
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from server_storage import PORT, ADDR, check_request, err_presence_response, \
    size_of_recv, argv
import logs.server_log_config

LOG = logging.getLogger('app.server')

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
    req = json.loads(client_socket.recv(size_of_recv).decode('utf-8'))
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
