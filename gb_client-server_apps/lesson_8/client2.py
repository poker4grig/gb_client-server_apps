import time
import sys
import logging
from socket import socket, AF_INET, SOCK_STREAM
from functions_client import message_from_server, check_presence_message, \
    create_message
from functions_server import get_message, send_message
from constants_client import PRESENCE_MSG, PORT, ADDR, ARGV_CLIENT
import logs.client_log_config

# инициализируем логгер для сервера
LOG = logging.getLogger("app.client")
LOG.info(
        f'Запущен клиент с парамертами: адрес сервера: {ARGV_CLIENT.addr}, '
        f'порт: {ARGV_CLIENT.port}, режим работы: {ARGV_CLIENT.mode}')


def client_2(presence_msg=PRESENCE_MSG):
    # user = input("Введите свое имя... ")  # Выключить лоя командной строки
    user = ARGV_CLIENT.user  # Включить лоя командной строки
    print("Клиент с именем: ", user)
    time.sleep(5)
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

    ARGV_CLIENT.mode = 'listen'  # потом удалить
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
                LOG.error(f'Соединение с сервером {ARGV_CLIENT.addr} было потеряно.')
                sys.exit(1)


if __name__ == '__main__':
    client_2()
