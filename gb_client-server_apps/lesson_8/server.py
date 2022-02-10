import logging
from select import select
import time
from functions_server import check_request, new_server_socket, get_message, \
    send_message
from constants_server import ADDR, PORT, SOCK_SET_TIMEOUT, COUNT_OF_LISTENING,\
    NEED_AUTHORIZATION, ARGV_SERVER
import logs.server_log_config

# инициализируем логгер для сервера
LOG = logging.getLogger('app.server')
# to_monitor - список сокетов, за которыми будет следить функция select
to_monitor = []


def accept_connection(server_sock):
    try:
        client_socket, client_addr = server_sock.accept()
        to_monitor.append(client_socket)
    except OSError:
        pass
    else:
        LOG.info(f'Установлено соединение с ПК {client_addr}')


def server_recv_send_message():
    # messages - очередь сообщений
    messages = []
    while True:
        r_from_cl = []
        w_to_cl = []
        cl_errors = []
        try:
            if to_monitor:
                r_from_cl, w_to_cl, cl_errors = select(to_monitor, to_monitor,
                                                       [])
        except OSError:
            pass
        # принимаем сообщения и если там есть сообщения,
        # кладём в словарь, если ошибка, исключаем клиента.
        if r_from_cl:
            for client_msg_socket in r_from_cl:
                try:
                    # Получаем сообщение от конкретного клиента
                    if client_msg_socket is server_socket:
                        accept_connection(client_msg_socket)
                    else:
                        request = get_message(client_msg_socket)
                        LOG.info(
                            f'От клиента {client_msg_socket.getpeername()} '
                            f'поступило сообщение: {request}')
                        # Проверяем сообщение на валидность
                        check_request(request, client_msg_socket, messages,
                                      to_monitor)
                except:
                    LOG.info(
                        f'Клиент {client_msg_socket.getpeername()} '
                        f'отключился от сервера.')
                    to_monitor.remove(client_msg_socket)

        if w_to_cl and messages:
            # Если есть сообщения для отправки и ожидающие клиенты,
            # отправляем им сообщение.
            msg_to_cl = {
                "action": 'msg',
                "time": time.time(),
                "user": messages[0]['user'],
                "text": messages[0]['text']
            }

            del messages[0]
            for waiting_client in w_to_cl:
                if waiting_client is server_socket:
                    accept_connection(waiting_client)
                else:
                    try:
                        send_message(waiting_client, msg_to_cl)
                        LOG.info(
                            f"Клиенту {waiting_client.getpeername()} "
                            f"отправлено сообщение {msg_to_cl}")
                    except:
                        LOG.info(
                            f'Клиент {waiting_client.getpeername()} '
                            f'отключился от сервера.')
                        to_monitor.remove(waiting_client)


# NEED_AUTHORIZATION?


if __name__ == '__main__':
    # получение серверного сокета из функции new_server_socket
    server_socket = new_server_socket(ADDR, PORT, COUNT_OF_LISTENING,          #  выключить для командной строки
                                      SOCK_SET_TIMEOUT)

    # server_socket = new_server_socket(ARGV_SERVER.addr, ARGV_SERVER.port,    #  включить для командной строки
    #                                   COUNT_OF_LISTENING, SOCK_SET_TIMEOUT)

    LOG.info(f'Запущен сервер с адресом: {ADDR}, портом {PORT}')
    # LOG.info(f'Запущен сервер с адресом: {ARGV_SERVER.addr}, '               #  включить логгер для командной строки
    #          f'портом {ARGV_SERVER.port}')
    to_monitor.append(server_socket)
    server_recv_send_message()


