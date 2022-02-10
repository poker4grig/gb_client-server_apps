import argparse
import time

ADDR = '0.0.0.0'
PORT = 7777
SIZE_OF_RECV = 4096
NEED_AUTHORIZATION = True
COUNT_OF_LISTENING = 5
SOCK_SET_TIMEOUT = 0.2

argv_parser = argparse.ArgumentParser(
    prog='command_line_server',
    description='аргументы командной строки сервера',
    epilog='автор - poker4grig'
)
argv_parser.add_argument('-a', '--addr', nargs='?', default=ADDR, help='help')
argv_parser.add_argument('-p', '--port', nargs='?', default=PORT, type=int,
                         help='help')
argv_parser.add_argument('-m', '--mode', nargs='?', default='listen',
                         help='help')
argv_parser.add_argument('-u', '--user', nargs='?', default='', help='help')
ARGV_SERVER = argv_parser.parse_args()

# contact_list - словарь с данными о пользователях - ключ - имя пользователя,
# значение - кортеж ("пароль", "статус")
CONTACT_LIST = {'poker4grig': ("1", "offline")}

RESPONSE_CODE_ALERT = {
    100: "basic notification ",
    101: "important notice",
    200: 'OK',
    201: "object created",
    202: "accepted",
    400: "wrong request/JSON object",
    401: "not authorized",
    402: "wrong login/password",
    403: "user forbidden",
    404: "user/chat is missing from the server",
    409: "there is already a connection with this login",
    410: "destination exists but is not available (offline)",
    500: "server error"
}

PROBE = {
    "action": "probe",
    "time": time.time()
}

PRESENCE_RESPONSE = (
    {"response": 200, "time": time.time(),
     "alert": RESPONSE_CODE_ALERT[200]})

ERR_PRESENCE_RESPONSE = (
    {"response": 400, "time": time.time(),
     "alert": RESPONSE_CODE_ALERT[400]})
