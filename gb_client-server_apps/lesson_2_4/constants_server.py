import time

ADDR = '0.0.0.0'
PORT = 7777
SIZE_OF_RECV = 4096
NEED_AUTHORIZATION = True
COUNT_OF_LISTENING = 5
SOCK_SET_TIMEOUT = 0.5
ENCODING = "utf-8"
TIMEOUT = 0.5
SERVER_DATABASE = 'sqlite:///server_base.db3'

# contact_list - словарь с данными о пользователях - ключ - имя пользователя,
# значение - кортеж ("пароль", "статус")
CONTACT_LIST = {'poker4grig': ("1", "offline")}

PROBE = {
    "action": "probe",
    "time": time.time()
}

PRESENCE_RESPONSE = {"response": 200}

ERR_PRESENCE_RESPONSE = {
    "response": 400,
    "error": None
}
