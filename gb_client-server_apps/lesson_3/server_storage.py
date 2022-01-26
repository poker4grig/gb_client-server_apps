import json
import time

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


def action_presence(request, contact_list):
    if "user" in request and "account_name" in request["user"]:
        if request["user"]["account_name"] in contact_list:
            contact_list[request["user"]["account_name"][1]] = "online"
        else:
            # добавляем пользователя в contact_list
            contact_list.update({request["user"]["account_name"]: ('None',
                                                                   'online')})
            print(contact_list)
    else:
        send_message = err_presence_response.encode('utf-8')
        return send_message
    send_message = presence_response.encode('utf-8')
    return send_message


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
