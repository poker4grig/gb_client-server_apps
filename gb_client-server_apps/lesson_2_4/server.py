import sys
import os
import json
import time
import argparse
import logging
from select import select
import threading
import configparser
import socket
import logs.server_log_config
from constants_server import PORT, TIMEOUT, PRESENCE_RESPONSE, \
    ERR_PRESENCE_RESPONSE, RESPONSE_202
from descriptors import Port, Host
from functions import get_message, send_message
from logs.log_decorator import log_func
from metaclasses import ServerVerifier
from server_database import ServerStorage
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from server_gui import MainWindow, gui_create_model, HistoryWindow, \
    create_stat_model, ConfigWindow
from PyQt5.QtGui import QStandardItemModel, QStandardItem


# инициализируем логгер для сервера
LOG = logging.getLogger('app.server')
new_connection = False
conflag_lock = threading.Lock()

@log_func
def server_argv(default_port, default_address):
    argv_parser = argparse.ArgumentParser(
        prog='command_line_server',
        description='аргументы командной строки сервера',
        epilog='автор - Григорьев Сергей'
    )
    argv_parser.add_argument('-p', default=default_port, type=int, nargs='?',
                              help='help')
    argv_parser.add_argument('-a', default=default_address, nargs='?',
                             help='help')
    namespace = argv_parser.parse_args(sys.argv[1:])
    listen_address = namespace.a
    listen_port = namespace.p
    return listen_address, listen_port


class Server(threading.Thread, metaclass=ServerVerifier):
    port = Port()
    # host = Host()

    def __init__(self, addr, port, database):

        self.server_socket = None
        self.host = addr
        self.port = port
        # база данных сервера
        self.database = database
        # self.clients - список подключенных клиентов
        self.clients = []
        # self.messages - очередь сообщений
        self.messages = []
        # self.names - словарь с именами пользователей и их сокетами
        self.names = {}
        super().__init__()

    def new_server_socket(self):
        """Метод возвращает серверный сокет для IPv4 и TCP протоколов, с
        опцией возможности повторного подключения к адресу, привязкой к
        адресу (address) и порту (port), прослушивающий определенное
        количество входящих подключений (listen), с установленным
        таймаутом (timeout)
        """
        LOG.info(
            f'Запущен сервер, порт для подключений: {self.port} , адрес с '
            f'которого принимаются подключения: {self.host}. Если адрес '
            f'не указан, принимаются соединения с любых адресов.')
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print(self.host)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.settimeout(TIMEOUT)
        self.server_socket.listen()

    def run(self):
        # Инициализация сокета
        self.new_server_socket()

        while True:
            try:
                client_socket, client_addr = self.server_socket.accept()
            except OSError:
                pass
            else:
                LOG.info(f'Установлено соединение с ПК {client_addr}')
                self.clients.append(client_socket)

            r_from_cl = []
            w_to_cl = []
            cl_errors = []
            try:
                if self.clients:
                    r_from_cl, w_to_cl, cl_errors = select(self.clients,
                                                           self.clients, [], 0)
            except OSError:
                pass
            # принимаем сообщения и если там есть сообщения, кладём в словарь,
            # если ошибка, исключаем клиента.
            if r_from_cl:
                for client_msg_socket in r_from_cl:
                    try:
                        self.process_client_message(
                            get_message(client_msg_socket),
                            client_msg_socket)
                    except (OSError):
                        LOG.info(f'Клиент {client_msg_socket.getpeername()} '
                                 f'отключился от сервера.')
                        for name in self.names:
                            if self.names[name] == client_msg_socket:
                                self.database.user_logout(name)
                                del self.names[name]
                                break
                        self.clients.remove(client_msg_socket)

            for mess in self.messages:
                try:
                    self.process_message(mess, w_to_cl)
                except (ConnectionAbortedError, ConnectionError, ConnectionResetError, ConnectionRefusedError):
                    LOG.info(
                        f'Связь с клиентом с именем {mess["to"]} была потеряна')
                    self.clients.remove(self.names[mess["to"]])
                    self.database.user_logout(mess["to"])
                    del self.names[mess["to"]]
            self.messages.clear()

    def process_message(self, message, listen_socks):
        """ Функция адресной отправки сообщения определённому клиенту. Принимает
        словарь сообщение, список зарегистрированных пользователей и слушающие
        сокеты. Ничего не возвращает.
        """
        if message["to"] in self.names and self.names[message["to"]] \
                in listen_socks:
            send_message(self.names[message["to"]], message)
            LOG.info(f'Отправлено сообщение пользователю {message["to"]} '
                     f'от пользователя {message["from"]}.')
        elif message["to"] in self.names and self.names[message["to"]] not in listen_socks:
            raise ConnectionError
        else:
            LOG.error(
                f'Пользователь {message["to"]} не зарегистрирован на сервере, '
                f'отправка сообщения невозможна.')

    def process_client_message(self, message, client):
        """Обработчик сообщений от клиентов, принимает словарь - сообщение от
        клиента, проверяет корректность, отправляет словарь-ответ в случае
        необходимости.
        """
        global new_connection
        LOG.debug(f'Разбор сообщения от клиента : {message}')
        # Если это сообщение о присутствии, принимаем и отвечаем
        if "action" in message and message["action"] == "presence" and \
                "time" in message and "user" in message:
            # Если такой пользователь ещё не зарегистрирован,
            # регистрируем, иначе отправляем ответ и завершаем соединение.
            if message["user"]["account_name"] not in self.names.keys():
                self.names[message["user"]["account_name"]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(message['user']['account_name'],
                                         client_ip, client_port)
                send_message(client, PRESENCE_RESPONSE)
                with conflag_lock:
                    new_connection = True
                return
            else:
                response = ERR_PRESENCE_RESPONSE
                response["error"] = 'Имя пользователя уже занято.'
                send_message(client, response)
                self.clients.remove(client)
                client.close()
            return
        # Если это сообщение, то добавляем его в очередь сообщений.
        # Ответ не требуется.
        elif "action" in message and message["action"] == "message" and \
                "to" in message and "time" in message \
                and "from" in message and "text" in message and \
                self.names[message["from"]] == client:
            self.messages.append(message)
            self.database.process_message(message["from"], message["to"])
            return
        # Если клиент выходит
        elif "action" in message and message["action"] == "exit" and \
                "account_name" in message and \
                self.names[message["account_name"]] == client:
            self.database.user_logout(message['account_name'])
            LOG.info(
                f'Клиент {message["account_name"]} корректно отключился от '
                f'сервера.')
            self.clients.remove(self.names[message["account_name"]])
            self.names[message["account_name"]].close()
            del self.names[message["account_name"]]
            with conflag_lock:
                new_connection = True
            return
        # Если это запрос контакт-листа
        elif 'action' in message and message[
            'action'] == 'get_contacts' and 'user' in message and \
                self.names[message['user']] == client:
            response = RESPONSE_202
            response['data_list'] = self.database.get_contacts(message['user'])
            send_message(client, response)
        # Если это добавление контакта
        elif 'action' in message and message['action'] == 'add' and \
                "account_name" in message and 'user' in message and \
                self.names[message['user']] == client:
            self.database.add_contact(message['user'], message["account_name"])
            send_message(client, PRESENCE_RESPONSE)
        # Если это удаление контакта
        elif 'action' in message and message['action'] == 'remove' and \
                "account_name" in message and 'user' in message and \
                self.names[message['user']] == client:
            self.database.remove_contact(message['user'], message["account_name"])
            send_message(client, PRESENCE_RESPONSE)

        # Если это запрос известных пользователей
        elif 'action' in message and message['action'] == 'get_users' and \
                "account_name" in message and \
                self.names[message["account_name"]] == client:
            response = RESPONSE_202
            response['data_list'] = [user[0] for user in
                                     self.database.users_list()]
            send_message(client, response)

        # Иначе отдаём Bad request
        else:
            response = ERR_PRESENCE_RESPONSE
            response["error"] = 'Запрос некорректен.'
            send_message(client, response)
            return
def main():
    # Загрузка файла конфигурации сервера
    config = configparser.ConfigParser()

    dir_path = os.path.dirname(os.path.realpath(__file__))
    config.read(f"{dir_path}/{'server.ini'}")

    listen_address, listen_port = server_argv(
        config['SETTINGS']['Default_port'], config['SETTINGS']['Listen_Address'])

    # инициализация БД
    database = ServerStorage(
        os.path.join(
            config['SETTINGS']['Database_path'],
            config['SETTINGS']['Database_file']))

    server = Server(listen_address, listen_port, database)
    server.daemon = True
    server.start()  # Запуск в отдельном потоке

    # Графическое окружение для сервера
    server_app = QApplication(sys.argv)
    main_window = MainWindow()  # Работает параллельно серверу
    # Инициализируем параметры в окна главного окна
    main_window.statusBar().showMessage('Server Working')  # Подвал
    # заполняем таблицу основного окна делаем разметку и заполняем
    main_window.active_clients_table.setModel(gui_create_model(database))
    main_window.active_clients_table.resizeColumnsToContents()
    main_window.active_clients_table.resizeRowsToContents()

    def list_update():
        # Функция обновляющяя,обновляет список подключённых, проверяет флаг
        # подключения, и при необходимости обновляет список
        global new_connection
        if new_connection:
            main_window.active_clients_table.setModel(
                gui_create_model(database))
            main_window.active_clients_table.resizeColumnsToContents()
            main_window.active_clients_table.resizeRowsToContents()
            with conflag_lock:
                new_connection = False

    def show_statistics():
        global stat_window
        stat_window = HistoryWindow()
        stat_window.history_table.setModel(create_stat_model(database))
        stat_window.history_table.resizeColumnsToContents()
        stat_window.history_table.resizeRowsToContents()
        # stat_window.show()

    def server_config():
        global config_window
        config_window = ConfigWindow()
        config_window.db_path.insert(config['SETTINGS']['Database_path'])
        config_window.db_file.insert(config['SETTINGS']['Database_file'])
        config_window.port.insert(config['SETTINGS']['Default_port'])
        config_window.ip.insert(config['SETTINGS']['Listen_Address'])
        config_window.save_btn.clicked.connect(save_server_config)

        # Функция сохранения настроек
    def save_server_config():
        global config_window
        message = QMessageBox()
        config['SETTINGS']['Database_path'] = config_window.db_path.text()
        config['SETTINGS']['Database_file'] = config_window.db_file.text()
        try:
            port = int(config_window.port.text())
        except ValueError:
            message.warning(config_window, 'Ошибка', 'Порт должен быть числом')
        else:
            config['SETTINGS']['Listen_Address'] = config_window.ip.text()
            if 1023 < port < 65536:
                config['SETTINGS']['Default_port'] = str(port)
                print(port)
                with open('server.ini', 'w') as conf:
                    config.write(conf)
                    message.information(
                        config_window, 'OK', 'Настройки успешно сохранены!')

            else:
                message.warning(
                    config_window,
                    'Ошибка',
                    'Порт должен быть от 1024 до 65536')

    # Таймер, обновляющий список клиентов 1 раз в секунду
    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)

    # Связываем кнопки и процедуры
    main_window.refresh_button.triggered.connect(list_update)
    main_window.show_history_button.triggered.connect(show_statistics)
    main_window.config_btn.triggered.connect(server_config)

    server_app.exec_()


if __name__ == '__main__':
    main()


