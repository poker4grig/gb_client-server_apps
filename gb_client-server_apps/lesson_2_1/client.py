import argparse
import json
import logging
import sys
import threading
import time
from socket import socket, AF_INET, SOCK_STREAM

from constants_client import PORT, ADDR
from errors import ServerError, ReqFieldMissingError
from functions_client import message_from_server, create_presence_message, \
    user_interactive, process_response_answer
from functions_server import get_message, send_message

# инициализируем логгер для сервера
LOG = logging.getLogger("app.client")


# @log_func
def client_argv():
    """Парсер аргументов коммандной строки для клиента"""
    argv_parser = argparse.ArgumentParser(
        prog='command_line_client',
        description='аргументы командной строки клиента',
        epilog='автор - poker4grig'
    )
    argv_parser.add_argument('-a', '--addr', nargs='?', default=ADDR,
                             help='help')
    argv_parser.add_argument('-p', '--port', nargs='?', default=PORT, type=int,
                             help='help')
    argv_parser.add_argument('-u', '--user', nargs='?', default='',
                             help='help')
    argv_client = argv_parser.parse_args()
    if not 1023 < argv_client.port < 65536:
        LOG.critical(
            f'Попытка запуска клиента с неподходящим номером порта: '
            f'{argv_client.port}. '
            f'Допустимы адреса с 1024 до 65535. Клиент завершается.')
        sys.exit(1)

    return argv_client


ARGV_CLIENT = client_argv()
user = ARGV_CLIENT.user
if ARGV_CLIENT.user == '':
    user = input("Введите свое имя... ")
    print("Клиент с именем: ", user)
print(f'Запущен клиент с параметрами: адрес сервера: {ARGV_CLIENT.addr}, '
      f'порт: {ARGV_CLIENT.port}, имя пользователя: {ARGV_CLIENT.user}')


def client_1():
    """Основная функция клиента"""
    connect_socket = socket(AF_INET, SOCK_STREAM)
    try:
        connect_socket.connect(
            (ARGV_CLIENT.addr, ARGV_CLIENT.port))  # Включить для ком.строки
        # connect_socket.connect((ADDR, PORT))  # Выключить для ком.строки

        LOG.info("Мы подключились к серверу")
        send_message(connect_socket, create_presence_message(user))
        LOG.info("На сервер отправлено приветственное сообщение")
        answer = process_response_answer(get_message(connect_socket))
        LOG.info(f'Установлено соединение с сервером. Ответ сервера: {answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        LOG.error('Не удалось декодировать полученную Json строку.')
        sys.exit(1)
    except ServerError as error:
        LOG.error(
            f'При установке соединения сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except ReqFieldMissingError as missing_error:
        LOG.error(
            f'В ответе сервера отсутствует необходимое поле {missing_error.missing_field}')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        LOG.critical(
            f'Не удалось подключиться к серверу {ARGV_CLIENT.addr}:{ARGV_CLIENT.port}, '
            f'конечный компьютер отверг запрос на подключение.')
        sys.exit(1)
    else:
        # запуск клиентского процесса приема сообщений
        receiver = threading.Thread(target=message_from_server,
                                    args=(connect_socket, user))
        receiver.daemon = True
        receiver.start()
        # запуск клиентского процесса отправки сообщений
        user_interface = threading.Thread(target=user_interactive,
                                          args=(connect_socket, user))
        user_interface.daemon = True
        user_interface.start()
        LOG.debug('Запущены процессы')

        while True:
            time.sleep(1)
            if receiver.is_alive() and user_interface.is_alive():
                continue
            else:
                break


if __name__ == '__main__':
    client_1()
