import logging
import sys
import time
from logs.log_decorator import log_func
from constants_server import RESPONSE_CODE_ALERT

LOG = logging.getLogger("app.client")


# @log_func
def check_presence_message(answer, code=RESPONSE_CODE_ALERT):
    if answer['response'] == 200:
        if answer['response'] == 200:
            return "Добро пожаловать! Доступ разрешен."
        elif answer['response'] == 400:
            return "Доступ запрещен", answer['alert']


# @log_func
def create_message(sock, user):
    message = input(
        'Введите сообщение для отправки или <quit> для завершения работы: ')
    if message == 'quit':
        sock.close()
        LOG.info('Завершение работы по команде пользователя.')
        sys.exit(0)
    message_dict = {
        "action": "msg",
        "time": time.time(),
        "user": user,
        "text": message
    }
    LOG.debug(f'Сформирован словарь сообщения: {message_dict}')
    return message_dict


# @log_func
def message_from_server(message):

    if "action" in message and message["action"] == "msg" and \
            "user" in message and "text" in message:
        print(f'Получено сообщение от пользователя '
              f'{message["user"]}:\n{message["text"]}')
        LOG.info(f'Получено сообщение от пользователя '
                    f'{message["user"]}:\n{message["text"]}')
    else:
        LOG.error(
            f'Получено некорректное сообщение с сервера: {message}')


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
