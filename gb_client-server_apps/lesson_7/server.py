import logging
import select
import time
from functions_server import check_request, new_server_socket, get_message, \
    send_message
from constants_server import ADDR, PORT, SOCK_SET_TIMEOUT, COUNT_OF_LISTENING,\
    NEED_AUTHORIZATION, ARGV_SERVER
import logs.server_log_config

# инициализируем логгер для сервера
LOG = logging.getLogger('app.server')


def server_recv_send_message(server_socket):
    # список клиентов, очередь сообщений
    clients = []
    messages = []
    while True:
        try:
            client, client_addr = server_socket.accept()
        except OSError:
            pass
        else:
            LOG.info(f'Установлено соединение с ПК {client_addr}')
            clients.append(client)
            # Проверяем на наличие ждущих клиентов
            r_from_cl = []
            w_to_cl = []
            cl_errors = []
            try:
                if clients:
                    r_from_cl, w_to_cl, cl_errors = select.select(clients,
                                                                  clients, [],
                                                                  0)
            except OSError:
                pass
            # принимаем сообщения и если там есть сообщения,
            # кладём в словарь, если ошибка, исключаем клиента.
            finally:
                if r_from_cl:
                    for client_msg_socket in r_from_cl:
                        try:
                            # Получаем сообщение от конкретного клиента
                            req = get_message(client_msg_socket)
                            LOG.info(
                                f'От клиента {client_msg_socket.getpeername()} '
                                f'поступило сообщение: {req}')
                            # Проверяем сообщение на валидность
                            check_request(req, client_msg_socket, messages, clients)
                        except:
                            LOG.info(
                                f'Клиент {client_msg_socket.getpeername()} '
                                f'отключился от сервера.')
                            clients.remove(client_msg_socket)

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
                        try:
                            send_message(waiting_client, msg_to_cl)
                            LOG.info(
                                f"Клиенту {waiting_client.getpeername()} "
                                f"отправлено сообщение {msg_to_cl}")
                        except:
                            LOG.info(
                                f'Клиент {waiting_client.getpeername()} '
                                f'отключился от сервера.')
                            clients.remove(waiting_client)


def event_loop():
    # получение серверного сокета из функции new_server_socket
    # выключить для командной строки
    server_socket = new_server_socket(ADDR, PORT, COUNT_OF_LISTENING,
                                      SOCK_SET_TIMEOUT)
    # включить для командной строки
    # server_socket = new_server_socket(ARGV_SERVER.addr, ARGV_SERVER.port,
    #                                   COUNT_OF_LISTENING, SOCK_SET_TIMEOUT)
    #  поменять логгер для командной строки
    LOG.info(f'Запущен сервер с адресом: {ADDR}, портом {PORT}')

    server_recv_send_message(server_socket)

# NEED_AUTHORIZATION?


if __name__ == '__main__':
    event_loop()

