import logging
import time
import argparse
from logs.log_decorator import log_func

ADDR = '127.0.0.1'
PORT = 7777

argv_parser = argparse.ArgumentParser(
    prog='command_line_client',
    description='аргументы командной строки клиента',
    epilog='автор - poker4grig'
)
argv_parser.add_argument('-a', '--addr', nargs='?', default=ADDR,
                         help='help')
argv_parser.add_argument('-p', '--port', nargs='?', default=PORT)
argv = argv_parser.parse_args()
LOG = logging.getLogger("app.client")

size_of_recv = 4096
current_user = ('poker4grig', "1")

presence_msg = {
    "action": "presence"
}

auth_msg = {
    "action": "authenticate"
}


@log_func
def send_message(msg):
    LOG.debug(
        f'В функцию <<{send_message.__name__}>> поступил шаблон сообщения: {msg}.')
    if msg["action"] == 'presence':
        msg["time"] = time.time()
        msg["type"] = "online"
        msg.update({"user": {"account_name": current_user[0],
                             "status": "In contact"}})
    elif msg["action"] == 'authenticate':
        msg["time"] = time.time()
        msg["type"] = 'online'
        msg.update({"user": {"account_name": current_user[0],
                             "password": current_user[1]}})
    else:
        LOG.critical(f'Сообщение не сформировано. Неверный шаблон!')
        return None
    LOG.info(
        f'Формирование сообщения для <<{msg["user"]["account_name"]}>> завершилось успешно.')
    return msg

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
