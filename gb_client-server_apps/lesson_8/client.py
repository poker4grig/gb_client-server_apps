import argparse
import logging
import sys
from socket import socket, AF_INET, SOCK_STREAM

import logs.client_log_config
from constants_client import PORT, ADDR
from functions_client import message_from_server, create_presence_message, \
    create_message
from functions_server import get_message, send_message

# инициализируем логгер для сервера
LOG = logging.getLogger("app.client")


def client_argv():
    argv_parser = argparse.ArgumentParser(
        prog='command_line_client',
        description='аргументы командной строки клиента',
        epilog='автор - poker4grig'
    )
    argv_parser.add_argument('-a', '--addr', nargs='?', default=ADDR,
                             help='help')
    argv_parser.add_argument('-p', '--port', nargs='?', default=PORT, type=int,
                             help='help')
    argv_parser.add_argument('-m', '--mode', nargs='?', default='send',
                             help='help')
    argv_parser.add_argument('-u', '--user', nargs='?', default='',
                             help='help')
    argv_client = argv_parser.parse_args()
    return argv_client


ARGV_CLIENT = client_argv()
LOG.info(
    f'Запущен клиент с парамертами: адрес сервера: {ARGV_CLIENT.addr}, '
    f'порт: {ARGV_CLIENT.port}, режим работы: {ARGV_CLIENT.mode}')


def client_1():
    # user = input("Введите свое имя... ")  # Выключить для командной строки
    user = ARGV_CLIENT.user  # Включить для командной строки
    print("Клиент с именем: ", user)
    connect_socket = socket(AF_INET, SOCK_STREAM)

    # проверка порта
    if not 1023 < ARGV_CLIENT.port < 65536:
        LOG.critical(
            f'Попытка запуска клиента с неподходящим номером порта: {ARGV_CLIENT}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)
    elif ARGV_CLIENT.mode not in ('listen', 'send'):
        LOG.critical(f'Указан недопустимый режим работы {ARGV_CLIENT.mode}, '
                     f'допустимые режимы: listen , send')
        sys.exit(1)
    else:
        # connect_socket.connect((ARGV_CLIENT.addr, ARGV_CLIENT.port))  # Включить для ком.строки
        connect_socket.connect((ADDR, PORT))  # Выключить для ком.строки
        LOG.info("Мы подключились к серверу")
        presence_msg = create_presence_message(user)
        send_message(connect_socket, presence_msg)
        LOG.info("На сервер отправлено приветственное сообщение")

    if ARGV_CLIENT.mode == 'send':
        print('Режим работы - отправка сообщений.')
    else:
        print('Режим работы - приём сообщений.')

    while True:
        # режим работы - отправка сообщений
        if ARGV_CLIENT.mode == 'send':
            try:
                send_message(connect_socket, create_message(connect_socket,
                                                            user=user))
            except:
                LOG.error(f'Соединение с сервером {ARGV_CLIENT.addr} '
                          f'было потеряно.')
                sys.exit(1)

        # режим работы приём:
        if ARGV_CLIENT.mode == 'listen':
            try:
                message_from_server(get_message(connect_socket))
            except:
                LOG.error(f'Соединение с сервером {ARGV_CLIENT.addr} было '
                          f'потеряно.')
                sys.exit(1)


if __name__ == '__main__':
    client_1()
