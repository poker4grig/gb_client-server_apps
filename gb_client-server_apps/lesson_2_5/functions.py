import json
import sys
from lesson_2_5.errors import ServerError
from lesson_2_5.constants_server import SIZE_OF_RECV, ENCODING
from lesson_2_5.errors import ServerError
from lesson_2_5.logs.log_decorator import log_func
sys.path.append('../')


@log_func
def get_message(client):
    encoded_response = client.recv(SIZE_OF_RECV)
    json_response = encoded_response.decode(ENCODING)
    response = json.loads(json_response)
    if isinstance(response, dict):
        return response
    else:
        raise TypeError


@log_func
def send_message(sock, message):
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
