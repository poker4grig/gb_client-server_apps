import logging
import argparse
from select import select
import sys
from functions_server import new_server_socket, get_message, \
    process_client_message, process_message
from constants_server import ADDR, PORT, SOCK_SET_TIMEOUT, COUNT_OF_LISTENING
import logs.server_log_config
from logs.log_decorator import log_func

# инициализируем логгер для сервера
LOG = logging.getLogger('app.server')


def server_argv():
    argv_parser = argparse.ArgumentParser(
        prog='command_line_server',
        description='аргументы командной строки сервера',
        epilog='автор - poker4grig'
    )
    argv_parser.add_argument('-a', '--addr', nargs='?', default='', help='help')
    argv_parser.add_argument('-p', '--port', nargs='?', default=PORT, type=int,
                             help='help')
    argv_parser.add_argument('-u', '--user', nargs='?', default='', help='help')
    argv_server = argv_parser.parse_args()
    if not 1023 < argv_server.port < 65536:
        LOG.critical(
            f'Попытка запуска сервера с указанием неподходящего порта '
            f'{argv_server.port}. '
            f'Допустимы адреса с 1024 до 65535.')
        sys.exit(1)

    return argv_server


ARGV_SERVER = server_argv()
LOG.info(
        f'Запущен сервер, порт для подключений: {ARGV_SERVER.port}, '
        f'адрес с которого принимаются подключения: {ARGV_SERVER.addr}. '
        f'Если адрес не указан, принимаются соединения с любых адресов.')


def server(server_sock):
    # clients - список подключенных клиентов
    clients = []
    # messages - очередь сообщений
    messages = []
    # names - словарь с именами пользователей и их сокетами
    names = {}
    while True:
        try:
            client_socket, client_addr = server_sock.accept()
        except OSError:
            pass
        else:
            LOG.info(f'Установлено соединение с ПК {client_addr}')
            clients.append(client_socket)
        r_from_cl = []
        w_to_cl = []
        cl_errors = []
        try:
            if clients:
                r_from_cl, w_to_cl, cl_errors = select(clients, clients,
                                                       [], 0)
        except OSError:
            pass
        # принимаем сообщения и если там есть сообщения, кладём в словарь,
        # если ошибка, исключаем клиента.
        if r_from_cl:
            for client_msg_socket in r_from_cl:
                try:
                    process_client_message(get_message(client_msg_socket),
                                           messages, client_msg_socket,
                                           clients, names)
                except Exception:
                    LOG.info(f'Клиент {client_msg_socket.getpeername()} '
                                f'отключился от сервера.')
                    clients.remove(client_msg_socket)

        for mess in messages:
            try:
                process_message(mess, names, w_to_cl)
            except Exception:
                LOG.info(
                    f'Связь с клиентом с именем {mess["to"]} была потеряна')
                clients.remove(names[mess["to"]])
                del names[mess["to"]]
        messages.clear()


if __name__ == '__main__':
    # получение серверного сокета из функции new_server_socket
    # server_socket = new_server_socket(ADDR, PORT, COUNT_OF_LISTENING,      #  выключить для командной строки
    #                                   SOCK_SET_TIMEOUT)
    server_socket = new_server_socket(ARGV_SERVER.addr, ARGV_SERVER.port,    #  включить для командной строки
                                      COUNT_OF_LISTENING, SOCK_SET_TIMEOUT)
    # LOG.info(f'Запущен сервер с адресом: {ADDR}, портом {PORT}')
    LOG.info(f'Запущен сервер с адресом: {ARGV_SERVER.addr}, '               #  включить логгер для командной строки
             f'портом {ARGV_SERVER.port}')
    server(server_socket)


