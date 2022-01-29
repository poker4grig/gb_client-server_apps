import json
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from server_storage import action_presence, err_presence_response, \
    contact_list, check_request, argv, number_of_listening, size_of_recv

need_authorization = True

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

try:
    if 1024 > int(argv.port) > 65535:  # Включить для командной строки
    # if 1024 > 7777 > 65535:  # Выключить
        raise ValueError
    server_socket.bind((argv.addr, int(argv.port))) # Включить для командной строки
    # server_socket.bind(('', 7777))  # Выключить
except ValueError:
    print('Значение порта должно быть между 1024 и 65535')
server_socket.listen(number_of_listening)

while True:
    client_socket, addr = server_socket.accept()
    req = json.loads(client_socket.recv(size_of_recv).decode('utf-8'))
    try:
        if check_request(req) is not None:
            if check_request(req) == 'close':
                client_socket.close()
            else:
                client_socket.send(check_request(req))
        else:
            raise ValueError
    except ValueError:
        client_socket.send(err_presence_response.encode('utf-8'))

# need_authorization?