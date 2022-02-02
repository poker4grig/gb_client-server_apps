import json
import logging
import time
import argparse
from logs.log_decorator import log_func

LOG = logging.getLogger('app.server')

ADDR = ''
PORT = 7777
size_of_recv = 4096

argv_parser = argparse.ArgumentParser(
    prog='command_line_server',
    description='аргументы командной строки сервера',
    epilog='автор - poker4grig'
)
argv_parser.add_argument('-a', '--addr', nargs='?', default=ADDR, help='help')
argv_parser.add_argument('-p', '--port', nargs='?', default=PORT, help='help')
argv = argv_parser.parse_args()
# contact_list - словарь с данными о пользователях - ключ - имя пользователя,
# значение - кортеж ("пароль", "статус")
contact_list = {'poker4grig': ("1", "offline")}

response_code_alert = {
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

probe = {
    "action": "probe",
    "time": time.time()
}

presence_response = json.dumps(
    {"response": 200, "time": time.time(),
     "alert": response_code_alert[200]})

err_presence_response = json.dumps(
    {"response": 400, "time": time.time(),
     "alert": response_code_alert[400]})


################################functions#####################################
@log_func
def check_request(request):
    checked_message = None
    if isinstance(request, dict) and "action" in request and "time" in request:
        # Получили правильный запрос
        if request["action"] == 'presence':
            checked_message = action_presence(request, contact_list)
        elif request["action"] == 'authenticate':
            pass
        elif request["action"] == 'msg':
            pass
        elif request["action"] == 'join':
            pass
        elif request["action"] == 'leave':
            pass
        elif request["action"] == 'quit':
            checked_message = 'close'
    return checked_message

@log_func
def action_presence(request, contact_list):
    if "user" in request and "account_name" in request["user"]:
        if request["user"]["account_name"] in contact_list:
            contact_list[request["user"]["account_name"][1]] = "online"
            LOG.info(
                f"Пользователь {request['user']['account_name']} имеет статус <онлайн>")
        else:
            LOG.info(
                f"Функция {action_presence.__name__} добавила пользователя {request['user']['account_name']} в контактный лист")
            contact_list.update({request["user"]["account_name"]: ('None',
                                                                   'online')})
            # print(contact_list)
    else:
        send_message = err_presence_response.encode('utf-8')
        return send_message
    send_message = presence_response.encode('utf-8')
    return send_message

@log_func
def action_authenticate(request):
    pass
    # if "user" in request:
    #     if request['user']['account_name'] in contact_list:
    #         if request['user']['password'] == contact_list[
    #             request['user']['account_name']]:
    #             auth_response = json.dumps(
    #                 {"response": 200, "time": time.time(),
    #                  "alert": response_code_alert[200]})    #
    #             client_socket.send(auth_response.encode('utf-8'))
    #         else:
    #             auth_response = json.dumps(
    #                 {"response": 402, "time": time.time(),
    #                  "alert": response_code_alert[402]})
    #             client_socket.send(auth_response.encode('utf-8'))
    # else:
    #     auth_response = json.dumps(
    #         {"response": 401, "time": time.time(),
    #          "alert": response_code_alert[401]})
    #     client_socket.send(auth_response.encode('utf-8'))
    # return response


def action_message():
    pass
