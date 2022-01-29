import logging
import time

LOG = logging.getLogger("app.client")

current_user = ('poker4grig', "1")
ADDR = '127.0.0.1'
PORT = 7777

presence_msg = {
    "action": "presence"
}

auth_msg = {
    "action": "authenticate"
}


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
