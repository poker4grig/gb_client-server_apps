import argparse
import logging
from select import select
import threading
import socket
import logs.server_log_config
from constants_server import PORT, TIMEOUT, PRESENCE_RESPONSE, \
    ERR_PRESENCE_RESPONSE
from descriptors import Port, Host
from functions import get_message, send_message
from logs.log_decorator import log_func
from metaclasses import ServerVerifier
from server_database import ServerStorage

# инициализируем логгер для сервера
LOG = logging.getLogger('app.server')


@log_func
def server_argv():
    argv_parser = argparse.ArgumentParser(
        prog='command_line_server',
        description='аргументы командной строки сервера',
        epilog='автор - Григорьев Сергей'
    )
    argv_parser.add_argument('-a', '--addr', nargs='?', default='127.0.0.1',
                             help='help')
    argv_parser.add_argument('-p', '--port', nargs='?', default=PORT, type=int,
                             help='help')
    argv_server = argv_parser.parse_args()
    return argv_server


class Server(threading.Thread, metaclass=ServerVerifier):
    port = Port()
    host = Host()

    def __init__(self, argv_server, database):

        self.server_socket = None
        self.host = argv_server.addr
        self.port = argv_server.port
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

    def main_loop(self):
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
                    except:
                        LOG.info(f'Клиент {client_msg_socket.getpeername()} '
                                 f'отключился от сервера.')
                        self.clients.remove(client_msg_socket)

            for mess in self.messages:
                try:
                    self.process_message(mess, w_to_cl)
                except:
                    LOG.info(
                        f'Связь с клиентом с именем {mess["to"]} была потеряна')
                    self.clients.remove(self.names[mess["to"]])
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
        LOG.debug(f'Разбор сообщения от клиента : {message}')
        # Если это сообщение о присутствии, принимаем и отвечаем
        if "action" in message and message["action"] == "presence" and \
                "time" in message and "user" in message:
            # Если такой пользователь ещё не зарегистрирован,
            # регистрируем, иначе отправляем ответ и завершаем соединение.
            if message["user"]["account_name"] not in self.names.keys():
                self.names[message["user"]["account_name"]] = client
                client_ip, client_port = client.getpeername()
                self.database.user_login(message['user']['account_name'], client_ip, client_port)
                send_message(client, PRESENCE_RESPONSE)
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
                and "from" in message and "text" in message:
            self.messages.append(message)
            return
        # Если клиент выходит
        elif "action" in message and message["action"] == "exit" and \
                "account_name" in message:
            self.database.user_logout(message['account_name'])
            self.clients.remove(self.names[message["account_name"]])
            self.names[message["account_name"]].close()
            del self.names[message["account_name"]]
            return
        # Иначе отдаём Bad request
        else:
            response = ERR_PRESENCE_RESPONSE
            response["error"] = 'Запрос некорректен.'
            send_message(client, response)
            return


def print_help():
    print('Поддерживаемые комманды:')
    print('users - список известных пользователей')
    print('connected - список подключенных пользователей')
    print('loghist - история входов пользователя')
    print('exit - завершение работы сервера.')
    print('help - вывод справки по поддерживаемым командам')


def main():
    database = ServerStorage()
    server = Server(server_argv(), database)
    server.daemon = True
    server.start()
    print_help()

    while True:
        command = input('Введите команду: ')
        if command == 'help':
            print_help()
        elif command == 'exit':
            break
        elif command == 'users':
            for user in sorted(database.users_list()):
                print(f'Пользователь {user[0]}, последний вход: {user[1]}')
        elif command == 'connected':
            for user in sorted(database.active_users_list()):
                print(
                    f'Пользователь {user[0]}, подключен: {user[1]}:{user[2]}, время установки соединения: {user[3]}')
        elif command == 'loghist':
            name = input(
                'Введите имя пользователя для просмотра истории. Для вывода всей истории, просто нажмите Enter: ')
            for user in sorted(database.login_history(name)):
                print(
                    f'Пользователь: {user[0]} время входа: {user[1]}. Вход с: {user[2]}:{user[3]}')
        else:
            print('Команда не распознана.')


if __name__ == '__main__':
    main()
