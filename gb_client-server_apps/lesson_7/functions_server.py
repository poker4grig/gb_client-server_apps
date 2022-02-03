import logging
from logs.log_decorator import log_func
from constants_server import CONTACT_LIST, ERR_PRESENCE_RESPONSE, PRESENCE_RESPONSE

LOG = logging.getLogger('app.server')


@log_func
def check_request(request):
    checked_message = None
    if isinstance(request, dict) and "action" in request and "time" in request:
        # Получили правильный запрос
        if request["action"] == 'presence':
            checked_message = action_presence(request, CONTACT_LIST)
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
            # print(CONTACT_LIST)
    else:
        send_message = ERR_PRESENCE_RESPONSE.encode('utf-8')
        return send_message
    send_message = PRESENCE_RESPONSE.encode('utf-8')
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
