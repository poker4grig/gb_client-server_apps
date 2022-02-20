import json
import logging
from constants_server import SIZE_OF_RECV, ENCODING
from logs.log_decorator import log_func

LOG = logging.getLogger('app.server')


@log_func
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


@log_func
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
