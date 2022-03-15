import socket
import sys
import time
import logging
import json
import threading
from PyQt5.QtCore import pyqtSignal, QObject

from lesson_2_5.errors import ServerError
from lesson_2_5.functions import send_message, get_message

sys.path.append('../')

LOG = logging.getLogger("app.client")
# Объект блокировки для работы с сокетом.
socket_lock = threading.Lock()


# Класс - Транспорт, отвечает за взаимодействие с сервером
class ClientTransport(threading.Thread, QObject):
    # Сигналы: новое сообщение и потеря соединения
    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, port, ip_address, database, username):
        # Вызываем конструктор предка
        threading.Thread.__init__(self)
        QObject.__init__(self)

        self.database = database
        self.username = username
        # Сокет для работы с сервером
        self.transport = None
        # Устанавливаем соединение:
        self.connection_init(port, ip_address)
        # Обновляем таблицы известных пользователей и контактов
        try:
            self.user_list_update()
            self.contacts_list_update()
        except OSError as err:
            if err.errno:
                LOG.critical(f'Потеряно соединение с сервером.')
                raise ServerError('Потеряно соединение с сервером!')
            LOG.error(
                'Timeout соединения при обновлении списков пользователей.')
        except json.JSONDecodeError:
            LOG.critical(f'Потеряно соединение с сервером.')
            raise ServerError('Потеряно соединение с сервером!')
            # Флаг продолжения работы транспорта.
        self.running = True

    # Функция инициализации соединения с сервером
    def connection_init(self, port, ip):
        # Инициализация сокета и сообщение серверу о нашем появлении
        self.transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Таймаут необходим для освобождения сокета.
        self.transport.settimeout(5)

        # Соединяемся, 5 попыток соединения, флаг успеха ставим в True если
        # удалось
        connected = False
        for i in range(5):
            LOG.info(f'Попытка подключения №{i + 1}')
            try:
                self.transport.connect((ip, port))
            except (OSError, ConnectionRefusedError):
                pass
            else:
                connected = True
                break
            time.sleep(1)
        if not connected:
            LOG.critical('Не удалось установить соединение с сервером')
            raise ServerError('Не удалось установить соединение с сервером')

        LOG.debug('Установлено соединение с сервером')

        try:
            with socket_lock:
                send_message(self.transport, self.create_presence())
                self.process_server_ans(get_message(self.transport))
        except (OSError, json.JSONDecodeError):
            LOG.critical('Потеряно соединение с сервером!')
            raise ServerError('Потеряно соединение с сервером!')

        LOG.info('Соединение с сервером успешно установлено.')

    def create_presence(self):
        out = {
            "action": "presence",
            "time": time.time(),
            "user": {
                "account_name": self.username
            }
        }
        LOG.debug(f'Сформировано "presence" сообщение для пользователя '
                  f'{self.username}')
        return out

    def process_server_ans(self, message):
        LOG.debug(f'Разбор сообщения от сервера: {message}')
        # Если это подтверждение чего-либо
        if "response" in message:
            if message["response"] == 200:
                return
            elif message["response"] == 400:
                raise ServerError(f'{message["error"]}')
            else:
                LOG.debug(f'Принят неизвестный код подтверждения '
                          f'{message["response"]}')

        # Если это сообщение от пользователя добавляем в базу, даём сигнал о
        # новом сообщении
        elif 'action' in message and message['action'] == 'message' and \
                'from' in message and "to" in message and 'text' in message \
                and message["to"] == self.username:
            LOG.debug(f'Получено сообщение от пользователя {message["from"]}:'
                      f'{message["text"]}')
            self.database.save_message(message['from'], 'in', message['text'])
            self.new_message.emit(message['from'])

            # Функция обновляющая контакт - лист с сервера
    def contacts_list_update(self):
        LOG.debug(f'Запрос контакт листа для пользователя {self.name}')
        req = {
            'action': 'get_contacts',
            'time': time.time(),
            'user': self.username
        }
        LOG.debug(f'Сформирован запрос {req}')
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        LOG.debug(f'Получен ответ {ans}')
        if 'response' in ans and ans['response'] == 202:
            for contact in ans['data_list']:
                self.database.add_contact(contact)
        else:
            LOG.error('Не удалось обновить список контактов.')

    # Функция обновления таблицы известных пользователей.
    def user_list_update(self):
        LOG.debug(f'Запрос списка известных пользователей {self.username}')
        req = {
            'action': 'get_users',
            'time': time.time(),
            'account_name': self.username,
        }
        with socket_lock:
            send_message(self.transport, req)
            ans = get_message(self.transport)
        if 'response' in ans and ans['response'] == 202:
            self.database.add_users(ans['data_list'])
        else:
            LOG.error('Не удалось обновить список известных пользователей.')

    # Функция сообщающая на сервер о добавлении нового контакта
    def add_contact(self, contact):
        LOG.debug(f'Создание контакта {contact}')
        req = {
            'action': 'add',
            'time': time.time(),
            'user': self.username,
            'account_name': contact
        }
        with socket_lock:
            send_message(self.transport, req)
            self.process_server_ans(get_message(self.transport))

    # Функция удаления клиента на сервере
    def remove_contact(self, contact):
        LOG.debug(f'Удаление контакта {contact}')
        req = {
            'action': 'remove',
            'time': time.time(),
            'user': self.username,
            'account_name': contact
        }
        with socket_lock:
            send_message(self.transport, req)
            self.process_server_ans(get_message(self.transport))

    # Функция закрытия соединения, отправляет сообщение о выходе.
    def transport_shutdown(self):
        self.running = False
        message = {
            'action': 'exit',
            'time': time.time(),
            'account_name': self.username
        }
        with socket_lock:
            try:
                send_message(self.transport, message)
            except OSError:
                pass
            LOG.debug('Транспорт завершает работу.')
            time.sleep(0.5)

        # Функция отправки сообщения на сервер
    def send_message(self, to, message):
        message_dict = {
            'action': 'message',
            'from': self.username,
            'to': to,
            'time': time.time(),
            'text': message
        }
        LOG.debug(f'Сформирован словарь сообщения: {message_dict}')

        # Ждем освобождения сокета для отправки сообщения
        with socket_lock:
            send_message(self.transport, message_dict)
            self.process_server_ans(get_message(self.transport))
            LOG.info(f'Отправлено сообщение для пользователя {to}')

    def run(self):
        LOG.debug('Запущен процесс - приёмник сообщений с сервера.')
        while self.running:
            time.sleep(1)
            with socket_lock:
                try:
                    self.transport.settimeout(0.5)
                    message = get_message(self.transport)
                except OSError as err:
                    if err.errno:
                        LOG.critical(f'Потеряно соединение с сервером.')
                        self.running = False
                        self.connection_lost.emit()
                # Проблемы с соединением
                except (ConnectionError, ConnectionAbortedError,
                        ConnectionResetError, json.JSONDecodeError, TypeError):
                    LOG.debug(f'Потеряно соединение с сервером.')
                    self.running = False
                    self.connection_lost.emit()
                # Если сообщение получено, то вызываем функцию обработчик:
                else:
                    LOG.debug(f'Принято сообщение с сервера: {message}')
                    self.process_server_ans(message)
                finally:
                    self.transport.settimeout(5)
