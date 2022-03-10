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
from client_database import ClientDatabase

LOG = logging.getLogger("app.client")

# Объект блокировки сокета и работы с БД
sock_lock = threading.Lock()
database_lock = threading.Lock()


class ClientSender(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock = sock
        self.database = database
        super().__init__()

    # Создание словаря с сообщением о выходе
    def create_exit_message(self):
        return {
            'action': 'exit',
            'time': time.time(),
            'account_name': self.account_name
        }

    # Запрос адресата сообщения, формирование сообщение и отправка на сервер
    def create_message(self):
        to = input('Введите получателя сообщения: ')
        message = input('Введите сообщение для отправки: ')

    # Проверка, что получатель существует
        with database_lock:
            if not self.database.check_user(to):
                LOG.error(f'Попытка отправить сообщение незарегистрированному '
                          f'получателю: {to}')
                return

        message_dict = {
            'action': 'message',
            'from': self.account_name,
            'to': to,
            'time': time.time(),
            'text': message
        }
        LOG.debug(f'Сформирован словарь сообщения: {message_dict}')
    # Сохраняем сообщение для истории
        with database_lock:
            self.database.save_message(self.account_name, to, message)

        # Дожидаемся освобождения сокета для отправки сообщения
        with database_lock:
            try:
                send_message(self.sock, message_dict)
                LOG.info(f'Отправлено сообщение для пользователя {to}')
            except OSError as err:
                if err.errno:
                    LOG.critical('Потеряно соединение с сервером.')
                    exit(1)
            else:
                LOG.error('Не удалось передать сообщение. Таймаут соединения')

    # Взаимодействие с пользователем, запрос команд, отправка сообщений
    def run(self):
        self.print_help()
        while True:
            command = input('Введите команду: ')
            if command == 'message':
                self.create_message()
            elif command == 'help':
                self.print_help()
            elif command == 'exit':
                with sock_lock:
                    try:
                        send_message(self.sock, self.create_exit_message())
                    except:
                        pass
                    print('Завершение соединения.')
                    LOG.info('Завершение работы по команде пользователя.')
                # Необходима задержка, чтобы сообщение о выходе ушло
                time.sleep(0.5)
                break

            elif command == 'contacts':
                with database_lock:
                    contacts_list = self.database.get_contacts()
                for contact in contacts_list:
                    print(contact)

                # Редактирование
            elif command == 'edit':
                self.edit_contacts()
            elif command == 'history':
                self.print_history()
            else:
                print('Команда не распознана, попробуйте снова. help - вывести'
                      ' поддерживаемые команды.')

    def print_help(self):
        print('Поддерживаемые команды:')
        print('message - отправить сообщение. Кому и текст будет запрошены '
              'отдельно.')
        print('history - история сообщений')
        print('contacts - список контактов')
        print('edit - редактирование списка контактов')
        print('help - вывести подсказки по командам')
        print('exit - выход из программы')

    def print_history(self):
        ask = input(
            'Показать входящие сообщения - in, исходящие - out, все - Enter: ')
        with database_lock:
            if ask == 'in':
                history_list = self.database.get_history(
                    to_who=self.account_name)
                for message in history_list:
                    print(f'\nСообщение от пользователя: {message[0]} от '
                          f'{message[3]}:\n{message[2]}')
            elif ask == 'out':
                history_list = self.database.get_history(
                    from_who=self.account_name)
                for message in history_list:
                    print(
                        f'\nСообщение пользователю: {message[1]} от '
                        f'{message[3]}:\n{message[2]}')
            else:
                history_list = self.database.get_history()
                for message in history_list:
                    print(
                        f'\nСообщение от пользователя: {message[0]}, '
                        f'пользователю {message[1]} от '
                        f'{message[3]}\n{message[2]}')

    def edit_contacts(self):
        ask = input('Для удаления введите del, для добавления add: ')
        if ask == 'del':
            edit = input('Введите имя удаляемого контакта: ')
            with database_lock:
                if self.database.check_contact(edit):
                    self.database.del_contact(edit)
                else:
                    LOG.error('Попытка удаления несуществующего контакта.')
        elif ask == 'add':
            edit = input('Введите имя создаваемого контакта: ')
            if self.database.check_user(edit):
                with database_lock:
                    self.database.add_contact(edit)
                with sock_lock:
                    try:
                        add_contact(self.sock, self.account_name, edit)
                    except ServerError:
                        LOG.error(
                            'Не удалось отправить информацию на сервер.')


class ClientReader(threading.Thread, metaclass=ClientVerifier):
    def __init__(self, account_name, sock, database):
        self.account_name = account_name
        self.sock = sock
        self.database = database
        super().__init__()

        # Цикл приема сообщений и вывода их в консоль. При потере соединения
        # завершается
    def run(self):
        while True:
        # Здесь ожидаем 1 секунду и снова пробуем захватить сокет. Без задержки
        # второй поток может достаточно долго ждать освобождения сокета.
            time.sleep(1)
            with sock_lock:
                try:
                    message = get_message(self.sock)
                # Если некорректное сообщение
                except IncorrectDataRecivedError:
                    LOG.error(f'Не удалось декодировать полученное сообщение.')
                # Вышел таймаут соединения
                except OSError as err:
                    if err.errno:
                        LOG.critical(f'Потеряно соединение с сервером.')
                        break
                # Проблемы с соединением
                except (ConnectionError, ConnectionAbortedError,
                        ConnectionResetError, json.JSONDecodeError):
                    LOG.critical(f'Потеряно соединение с сервером.')
                    break
            # Если сообщение корректное, то выводим в консоль и записываем в БД
                else:
                    if 'action' in message and message['action'] == 'message' \
                            and 'from' in message and 'to' in message \
                            and 'text' in message \
                            and message['to'] == self.account_name:
                        print(f'\nПолучено сообщение от пользователя '
                              f'{message["from"]}:\n{message["text"]}')
                        # Захватываем работу с базой данных и сохраняем в неё сообщение
                        with database_lock:
                            try:
                                self.database.save_message(message['from'],
                                                           self.account_name,
                                                           message["text"])
                            except:
                                LOG.error('Ошибка взаимодействия с базой данных')

                        LOG.info(f'Получено сообщение от пользователя '
                                 f'{message["from"]}:\n{message["text"]}')
                    else:
                        LOG.error(f'Получено некорректное сообщение с сервера:'
                                  f' {message}')


@log_func
def create_presence(account_name):
    out = {
        "action": "presence",
        "time": time.time(),
        "user": {
            "account_name": account_name
        }
    }
    LOG.debug(f'Сформировано "presence" сообщение для пользователя '
              f'{account_name}')
    return out

@log_func
def process_response_ans(message):
    LOG.debug(f'Разбор приветственного сообщения от сервера: {message}')
    if "response" in message:
        if message["response"] == 200:
            return '200 : OK'
        elif message["response"] == 400:
            raise ServerError(f'400 : {message["error"]}')
    raise ReqFieldMissingError("response")


@log_func
def client_argv():
    """Парсер аргументов командной строки для клиента"""
    argv_parser = argparse.ArgumentParser(
        prog='command_line_client',
        description='аргументы командной строки клиента',
        epilog='автор - Григорьев Сергей'
    )
    argv_parser.add_argument('addr', default=ADDR, nargs='?', help='help')
    argv_parser.add_argument('port', default=PORT, type=int, nargs='?',
                             help='help')
    argv_parser.add_argument('name', default=None, nargs='?', help='help')
    namespace = argv_parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        LOG.critical(
            f'Попытка запуска клиента с неподходящим номером порта: '
            f'{server_port}. Допустимы адреса с 1024 до 65535. '
            f'Клиент завершается.')
        exit(1)
    return server_address, server_port, client_name

# запрос контакт листа
def contact_list_request(sock, name):
    LOG.debug(f'Запрос контакт листа для пользователя {name}')
    req = {
        'action': 'get_contacts',
        'time': time.time(),
        'user': name
    }
    LOG.debug(f'Сформирован запрос {req}')
    send_message(sock, req)
    ans = get_message(sock)
    LOG.debug(f'Получен ответ {ans}')
    if 'response' in ans and ans['response'] == 202:
        return ans['data_list']
    else:
        raise ServerError

# Добавление пользователя в контакт лист
def add_contact(sock, username, contact):
    LOG.debug(f'Создание контакта {contact}')
    req = {
        'action': 'add',
        'time': time.time(),
        'user': username,
        'account_name': contact
    }
    send_message(sock, req)
    ans = get_message(sock)
    if 'response' in ans and ans['response'] == 200:
        pass
    else:
        raise ServerError('Ошибка создания контакта')
    print('Удачное создание контакта.')

    # Запрос списка известных пользователей
def user_list_request(sock, username):
    LOG.debug(f'Запрос списка известных пользователей {username}')
    req = {
        'action': 'get_users',
        'time': time.time(),
        'account_name': username
    }
    send_message(sock, req)
    ans = get_message(sock)
    if 'response' in ans and ans['response'] == 202:
        return ans['data_list']
    else:
        raise ServerError

# Удаление пользователя из контакт листа
def remove_contact(sock, username, contact):
    LOG.debug(f'Создание контакта {contact}')
    req = {
        'action': 'remove',
        'time': time.time(),
        'user': username,
        'account_name': contact
    }
    send_message(sock, req)
    ans = get_message(sock)
    if 'response' in ans and ans['response'] == 200:
        pass
    else:
        raise ServerError('Ошибка удаления контакта')
    print('Удачное удаление')

# Инициализация БД. Запускается при запуске, загружает данные в базу с сервера.
def database_load(sock, database, username):
    # Загружаем список известных пользователей
    try:
        users_list = user_list_request(sock, username)
    except ServerError:
        LOG.error('Ошибка запроса списка известных пользователей.')
    else:
        database.add_users(users_list)

    # Загружаем список контактов
    try:
        contacts_list = contact_list_request(sock, username)
    except ServerError:
        LOG.error('Ошибка запроса списка контактов.')
    else:
        for contact in contacts_list:
            database.add_contact(contact)


def main():
    print('Консольный мессенджер. Клиентский модуль.')
    server_address, server_port, client_name = client_argv()

    if not client_name:
        client_name = input('Введите имя пользователя: ')
    else:
        print(f'Клиентский модуль запущен с именем: {client_name}')
    print("Имя пользователя: ", client_name)
    LOG.info(
        f'Запущен клиент с параметрами: адрес сервера: {server_address} , '
        f'порт: {server_port}, имя пользователя: {client_name}')

    # Инициализация сокета и приветственное сообщение
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Таймаут для освобождения сокета.
        sock.settimeout(1)

        sock.connect((server_address, server_port))
        send_message(sock, create_presence(client_name))
        answer = process_response_ans(get_message(sock))
        LOG.info(f'Установлено соединение с сервером. Ответ сервера: '
                 f'{answer}')
        print(f'Установлено соединение с сервером.')
    except json.JSONDecodeError:
        LOG.error('Не удалось декодировать полученную Json строку.')
        exit(1)
    except ServerError as error:
        LOG.error(f'При установке соединения сервер вернул ошибку: '
                  f'{error.text}')
        exit(1)
    except ReqFieldMissingError as missing_error:
        LOG.error(f'В ответе сервера отсутствует необходимое поле '
                  f'{missing_error.missing_field}')
        exit(1)
    except (ConnectionRefusedError, ConnectionError):
        LOG.critical(
            f'Не удалось подключиться к серверу '
            f'{server_address}:{server_port}, конечный компьютер отверг '
            f'запрос на подключение.')
        exit(1)
    else:
    # Инициализация БД
        database = ClientDatabase(client_name)
        database_load(sock, database, client_name)

    # При корректном соединении с сервером запускаем поток взаимодействия с
    # пользователем
        module_sender = ClientSender(client_name, sock, database)
        module_sender.daemon = True
        module_sender.start()
        LOG.debug('Запущены процессы')
    # Запуск потока приема сообщений
        module_receiver = ClientReader(client_name, sock, database)
        module_receiver.daemon = True
        module_receiver.start()

    # Основной цикл потоков
        while True:
            time.sleep(1)
            if module_receiver.is_alive() and module_sender.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
