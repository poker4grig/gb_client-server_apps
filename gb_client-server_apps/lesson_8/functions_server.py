import json
import logging
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from constants_server import SIZE_OF_RECV, PRESENCE_RESPONSE, ENCODING, \
    ERR_PRESENCE_RESPONSE
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
    server_socket.bind((address, port))
    server_socket.settimeout(timeout)
    server_socket.listen(listen)
    return server_socket


# @log_func
def get_message(client):
    try:
        encoded_request = client.recv(SIZE_OF_RECV)
        if isinstance(encoded_request, bytes):
            json_request = encoded_request.decode(ENCODING)
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
            encoded_message = json_message.encode(ENCODING)
            client.send(encoded_message)
        else:
            raise ValueError
    except ValueError:
        LOG.error("Ваше сообщение не является словарем")


# @log_func
def process_client_message(message, messages_list, client, clients, names):
    """Обработчик сообщений от клиентов, принимает словарь - сообщение от
    клиента, проверяет корректность, отправляет словарь-ответ в случае
    необходимости.
    """
    LOG.debug(f'Разбор сообщения от клиента : {message}')
    # Если это сообщение о присутствии, принимаем и отвечаем
    if "action" in message and message["action"] == "presence" and \
            "time" in message and "user" in message:
        # Если такой пользователь ещё не зарегистрирован,
        # регистрируем, иначе отправляем ответ и завершаем соединение.
        if message["user"]["account_name"] not in names:
            names[message["user"]["account_name"]] = client
            send_message(client, PRESENCE_RESPONSE)
        else:
            response = ERR_PRESENCE_RESPONSE
            response["error"] = 'Имя пользователя уже занято.'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    # Если это сообщение, то добавляем его в очередь сообщений.
    # Ответ не требуется.
    elif "action" in message and message["action"] == "msg" and \
            "to" in message and "time" in message \
            and "from" in message and "text" in message:
        messages_list.append(message)
        return
    # Если клиент выходит
    elif "action" in message and message["action"] == "exit" and \
            "account_name" in message:
        clients.remove(names[message["account_name"]])
        names[message["account_name"]].close()
        del names[message["account_name"]]
        return
    # Иначе отдаём Bad request
    else:
        response = ERR_PRESENCE_RESPONSE
        response["error"] = 'Запрос некорректен.'
        send_message(client, response)
        return


# @log_func
def process_message(message, names, listen_socks):
    """ Функция адресной отправки сообщения определённому клиенту. Принимает
    словарь сообщение, список зарегистрированных пользователей и слушающие
    сокеты. Ничего не возвращает.
    """
    if message["to"] in names and names[message["to"]] in listen_socks:
        send_message(names[message["to"]], message)
        LOG.info(f'Отправлено сообщение пользователю {message["to"]} '
                    f'от пользователя {message["from"]}.')
    elif message["to"] in names and names[message["to"]] not in listen_socks:
        raise ConnectionError
    else:
        LOG.error(
            f'Пользователь {message["to"]} не зарегистрирован на сервере, '
            f'отправка сообщения невозможна.')

