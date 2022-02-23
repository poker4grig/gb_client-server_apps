import argparse
import json
import logging
import socket
import sys
import threading
import time

from constants_client import PORT, ADDR
from descriptors import Port
from errors import IncorrectDataRecivedError, ReqFieldMissingError, ServerError
from functions import get_message, send_message
from logs.log_decorator import log_func
from metaclasses import ClientVerifier

LOG = logging.getLogger("app.client")


@log_func
def client_argv():
    """Парсер аргументов командной строки для клиента"""
    argv_parser = argparse.ArgumentParser(
        prog='command_line_client',
        description='аргументы командной строки клиента',
        epilog='автор - Григорьев Сергей'
    )
    argv_parser.add_argument('-a', '--addr', nargs='?', default=ADDR,
                             help='help')
    argv_parser.add_argument('-p', '--port', nargs='?', default=PORT, type=int,
                             help='help')
    argv_parser.add_argument('-u', '--user', nargs='?', default=None,
                             help='help')
    argv_client = argv_parser.parse_args()
    return argv_client


class Client(metaclass=ClientVerifier):
    port = Port()

    def __init__(self, argv_client):
        self.addr = argv_client.addr
        self.port = argv_client.port
        self.client_name = argv_client.user

    def print_help(self):
        """Функция выводящая справку по использованию"""
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены '
              'отдельно.')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    def create_exit_message(self, account_name):
        return {"action": "exit", "time": time.time(),
                "account_name": account_name}

    def create_message(self, sock, account_name='Guest'):
        """ Функция формирования и отправки сообщения конкретному пользователю.
                """
        to_user = input(
            'Введите имя пользователя, которому хотите отправить сообщение: ')
        message = input('Введите сообщение: ')

        message_dict = {"action": "message", "time": time.time(),
                        "from": account_name, "to": to_user, "text": message}
        LOG.debug(f'Создано сообщение {message_dict}')
        try:
            send_message(sock, message_dict)
            LOG.info(f'Отправлено сообщение({message}) пользователю:{to_user}')
        except:
            LOG.critical('Потеряно соединение с сервером')
            sys.exit(1)

    def instructions_for_user(self, sock):
        """ Инструкции пользователю по выбору команд для работы мессенджера """
        self.print_help()
        while True:
            command = input('Введите команду:  \n')
            if command == 'message':
                self.create_message(sock, self.client_name)
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                message_exit = self.create_exit_message(self.client_name)
                send_message(sock, message_exit)
                username = {'username': self.client_name}
                LOG.info(f'Пользователь {username} вышел из мессенджера')
                time.sleep(0.5)
                break
            else:
                print('Введенная команда недоступна. '
                      'Введите help для просмотра доступных команд')

    def user_interaction(self, sock):
        """ Функция получения и разбора сообщения от другого пользователя """
        while True:
            try:
                message = get_message(sock)
                if "action" in message and message[
                    "action"] == "message" and "from" in message and "text" \
                        in message and "to" in message and \
                        message["to"] == self.client_name:
                    print(
                        f'Получено сообщение от пользователя {message["from"]}:'
                        f'\n{message["text"]}')
                    LOG.info(
                        f'Получено сообщение от пользователя {message["from"]}:'
                        f'\n{message["text"]}')
                else:
                    LOG.error(
                        f'От сервера получено некорректное сообщение:{message}')
            except IncorrectDataRecivedError:
                LOG.error(f'Не удалось декодировать полученное сообщение.')
            except (OSError, ConnectionError, ConnectionAbortedError,
                    ConnectionResetError, json.JSONDecodeError):
                LOG.critical(f'Потеряно соединение с сервером.')
                break

    def create_presence(self, account_name='Guest'):
        return {"action": "presence", "time": time.time(),
                "user": {"account_name": self.client_name}}

    def response_from_server(self, message):
        """ Функция разбора приветственного сообщения от сервера """
        LOG.debug(f'Разбор приветственного сообщения от сервера: {message}')
        if "response" in message:
            if message["response"] == 200:
                return '200 : OK'
            elif message["response"] == 400:
                raise ServerError(f'400 : {message["error"]}')
        raise ReqFieldMissingError("response")

    def main(self):
        """ Функция инициации сокета, отправки приветственного сообщения
        серверу, получения от него ответа, создания потоков для приема и
        отправки сообщений другому пользователю
        """
        print('Консольный мессенджер. Клиентский модуль.')
        print("Имя пользователя: ", self.client_name)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.addr, self.port))
            presence_message = self.create_presence()
            send_message(sock, presence_message)
            answer = self.response_from_server(get_message(sock))
            LOG.info(
                f'Установлено соединение с сервером. Ответ от сервера {answer}')
            print('Соединение с сервером установлено')

        except json.JSONDecodeError:
            LOG.error('Не удалось декодировать полученную Json строку.')
            sys.exit(1)
        except ServerError as error:
            LOG.error(
                f'При установке соединения сервер вернул ошибку: {error.text}')
            sys.exit(1)
        except ReqFieldMissingError as missing_error:
            LOG.error(f'В ответе сервера отсутствует необходимое поле '
                      f'{missing_error.missing_field}')
            sys.exit(1)
        except ConnectionRefusedError:
            LOG.critical(
                f'Не удалось подключиться к серверу {self.address}:{self.port}, '
                f'конечный компьютер отверг запрос на подключение.')
            sys.exit(1)
        else:
            receiver = threading.Thread(
                target=self.user_interaction, args=(sock,))
            # receiver.daemon = True
            receiver.start()
            sender = threading.Thread(target=self.instructions_for_user,
                                      args=(sock,))
            # sender.daemon = True
            sender.start()
            LOG.debug('Потоки запущены')


@log_func
def main():
    argv_parser = client_argv()
    if not argv_parser.user:
        argv_parser.user = input('Введите имя пользователя: ')
    LOG.info(
        f'Запущен клиент с ip-адресом{argv_parser.addr}, порт:{argv_parser.port},'
        f'с именем:{argv_parser.user}')
    client = Client(argv_parser)
    client.main()


if __name__ == '__main__':
    main()
