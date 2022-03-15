import time

ADDR = '0.0.0.0'
PORT = 7777
SIZE_OF_RECV = 1024
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

# Словари - ответы:
# 200
RESPONSE_200 = {'response': 200}
# 202
RESPONSE_202 = {'response': 202,
                'data_list':None
                }
# 400
RESPONSE_400 = {
            'response': 400,
            'error': None
        }