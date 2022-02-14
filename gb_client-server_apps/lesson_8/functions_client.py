import logging
import sys
import time
import json
from errors import ServerError, ReqFieldMissingError, IncorrectDataRecivedError
from functions_server import get_message, send_message
from constants_server import RESPONSE_CODE_ALERT
from lesson_8.logs.log_decorator import log_func

LOG = logging.getLogger("app.client")


# @log_func
def create_presence_message(account_name):
    """Функция генерирует запрос о присутствии клиента"""
    presence_msg = {
        "action": "presence",
        "time": time.time(),
        "type": "online",
        "user": {
            "account_name": account_name
        }
    }
    LOG.debug(
        f'Сформировано {presence_msg} сообщение для пользователя {account_name}')
    return presence_msg


# @log_func
def create_message(sock, user):
    """Функция запрашивает кому отправить сообщение и само сообщение,
       и отправляет полученные данные на сервер"""
    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение для отправки: ')
    message_dict = {
        "action": "msg",
        "from": user,
        "to": to_user,
        "time": time.time(),
        "text": message
    }
    LOG.debug(f'Сформирован словарь сообщения: {message_dict}')
    try:
        send_message(sock, message_dict)
        LOG.info(f'Отправлено сообщение для пользователя {to_user}')
    except:
        LOG.critical('Потеряно соединение с сервером.')
        sys.exit(1)


# @log_func
def message_from_server(sock, username):
    """Функция - обработчик сообщений других пользователей, поступающих с
    сервера
    """
    while True:
        try:
            message = get_message(sock)
            if "action" in message and message["action"] == "msg" and \
                    "from" in message and "to" in message \
                    and "text" in message and message["to"] == username:
                print(
                    f'\nПолучено сообщение от пользователя {message["from"]}:'
                    f'\n{message["text"]}')
                LOG.info(
                    f'Получено сообщение от пользователя {message["from"]}:'
                    f'\n{message["text"]}')
            else:
                LOG.error(
                    f'Получено некорректное сообщение с сервера: {message}')
        except IncorrectDataRecivedError:
            LOG.error(f'Не удалось декодировать полученное сообщение.')
        except (OSError, ConnectionError, ConnectionAbortedError,
                ConnectionResetError, json.JSONDecodeError):
            LOG.critical(f'Потеряно соединение с сервером.')
            break


# @log_func
def process_response_answer(message):
    """Функция разбирает ответ сервера на сообщение о присутствии,
    возвращает 200 если все ОК или генерирует исключение при ошибке
    """
    LOG.debug(
        f'Разбор приветственного сообщения от сервера: {message}')
    if "response" in message:
        if message["response"] == 200:
            print("Добро пожаловать! Доступ разрешен.")
            return RESPONSE_CODE_ALERT[200]
        elif message["response"] == 400:
            raise ServerError(f'400 : {RESPONSE_CODE_ALERT[400]}')
    raise ReqFieldMissingError("response")


# @log_func
def user_interactive(sock, username):
    """Функция взаимодействия с пользователем"""
    print_help()
    while True:
        command = input('Введите команду: ')
        if command == 'msg':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, create_exit_message(username))
            print('Завершение соединения.')
            LOG.info('Завершение работы по команде пользователя.')
            # Задержка неоходима, чтобы успело уйти сообщение о выходе
            time.sleep(0.5)
            break
        else:
            print('Команда не распознана, попробуйте снова. help - вывести '
                  'поддерживаемые команды.')


def print_help():
    """Функция выводящая справку по использованию"""
    print('Поддерживаемые команды:')
    print('msg - отправить сообщение. Кому и текст будет запрошены '
          'отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


# @log_func
def create_exit_message(account_name):
    return {
        "action": "exit",
        "time": time.time(),
        "account_name": account_name
    }

# presence_msg = {
#     "action": "presence",
#     "time": time.time(),
#     "type": "online",
#     "user": {
#         "account_name": "222",
#         "status": "In contact"
#     }
# }
# auth_msg = {
#     "action": "authenticate",
#     "time": time.time(),
#     "user": {
#         "account_name": current_user[0],
#         "password": current_user[1]
#     }
# }
