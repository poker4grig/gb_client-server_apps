import logging
import time
from logs.log_decorator import log_func
from constants_client import CURRENT_USER

LOG = logging.getLogger("app.client")


@log_func
def send_message(msg):
    LOG.debug(
        f'В функцию <<{send_message.__name__}>> поступил шаблон сообщения: {msg}.')
    if msg["action"] == 'presence':
        msg["time"] = time.time()
        msg["type"] = "online"
        msg.update({"user": {"account_name": CURRENT_USER[0],
                             "status": "In contact"}})
    elif msg["action"] == 'authenticate':
        msg["time"] = time.time()
        msg["type"] = 'online'
        msg.update({"user": {"account_name": CURRENT_USER[0],
                             "password": CURRENT_USER[1]}})
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
