import json
import logging
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR

from constants_server import CONTACT_LIST,  SIZE_OF_RECV, PRESENCE_RESPONSE, \
    ERR_PRESENCE_RESPONSE, ARGV_SERVER
from logs.log_decorator import log_func

LOG = logging.getLogger('app.server')


# @log_func
def new_server_socket(address, port, listen, timeout):
    """Функция возвращает серверный сокет для IPv4 и TCP протоколов, с опцией
    возможности повторного подключения к адресу, привязкой к адресу (address) и
    порту (port), прослушивающий определенное количество входящих подключений
    (listen), с установленным таймаутом (timeout)
    """
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    try:
        if 1024 > port > 65535:
            raise ValueError
        server_socket.bind((address, port))
    except ValueError:
        LOG.critical(
            f'Порт № {port} не подходит для подключения. Значение порта должно'
            f' быть между 1024 и 65535')
    server_socket.settimeout(timeout)
    server_socket.listen(listen)

    return server_socket


# @log_func
def get_message(client, size_of_recv=SIZE_OF_RECV):
    try:
        encoded_request = client.recv(SIZE_OF_RECV)
        if isinstance(encoded_request, bytes):
            json_request = encoded_request.decode("utf-8")
            request = json.loads(json_request)
            if isinstance(request, dict):
                return request
        raise ValueError
    except ValueError:
        LOG.error(f"Сообщение от {client.getpeername()} не является "
                  f"словарем")


# @log_func
def send_message(client, message):
    try:
        if isinstance(message, dict):
            json_message = json.dumps(message)
            encoded_message = json_message.encode("utf-8")
            client.send(encoded_message)
        else:
            raise ValueError
    except ValueError:
        LOG.error("Ваше сообщение не является словарем")


# @log_func
def check_request(request, client_socket, messages, clients,
                  contact_list=CONTACT_LIST, err_msg=ERR_PRESENCE_RESPONSE,
                  pres_msg=PRESENCE_RESPONSE):
    try:
        if "action" in request and "time" in request:
            # Получили правильный запрос
            if request["action"] == 'presence':
                message = action_presence(request, CONTACT_LIST)
                send_message(client_socket, message)
            elif request["action"] == 'msg':
                messages.append(request)
            elif request["action"] == 'authenticate':
                pass
            elif request["action"] == 'join':
                pass
            elif request["action"] == 'leave':
                pass
            elif request["action"] == 'quit':
                LOG.info(
                    f"Клиент {client_socket.getpeername()}"
                    f" закрыл соединение")
                client_socket.close()
                clients.remove(client_socket)
        else:
            raise ValueError
    except ValueError:
        LOG.critical(
            f'Функция {check_request.__name__} отметила сообщение от '
            f'{client_socket.getpeername()} как некорректное!')
        send_message(client_socket, err_msg)
        LOG.info(
            f"Отправлено сообщение об ошибке: {err_msg}")


# @log_func
def action_presence(request, contact_list, err_msg=ERR_PRESENCE_RESPONSE,
                    pres_msg=PRESENCE_RESPONSE):
    if "user" in request and "account_name" in request["user"]:
        if request["user"]["account_name"] in contact_list:
            contact_list[request["user"]["account_name"][1]] = "online"
            LOG.info(
                f"Пользователь {request['user']['account_name']} имеет статус "
                f"<онлайн>")
        else:
            LOG.info(
                f"Функция {action_presence.__name__} добавила пользователя "
                f"{request['user']['account_name']} в контактный лист")
            contact_list.update({request["user"]["account_name"]: ('None',
                                                                   'online')})
    else:
        return err_msg
    return pres_msg


# @log_func
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
