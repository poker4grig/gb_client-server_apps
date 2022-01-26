from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import json
import time
# import argparse

from storage import response_code_alert

# argv_parser = argparse.ArgumentParser(
#     prog='command_line_server',
#     description='аргументы командной строки сервера',
#     epilog='автор - poker4grig'
# )
# argv_parser.add_argument('-a', '--addr', nargs='?', default='', help='help')
# argv_parser.add_argument('-p', '--port', nargs='?', default=7777, help='help')
# argv = argv_parser.parse_args()

contact_list = {'poker4grig': "1"}
need_authorization = True

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# server_socket.bind(('', 7777))
try:
    if 1024 > int("1000") > 65535:
        raise ValueError
    # server_socket.bind((argv.addr, int(argv.port)))
    server_socket.bind(('', 7777))
except ValueError:
    print('Значение порта должно быть между 1024 и 65535')
server_socket.listen(5)

# server_response_template = {
#     "action": "authenticate",
#     "time": time.ctime(time.time()),
#     "response": 200,
#     "alert": response_code_alert[200]
# }

while True:
    client_socket, addr = server_socket.accept()
    initial_request = (client_socket.recv(4096))
    print(initial_request)
    # try:
    #     if isinstance(initial_request, bytes):
    #         from_json_initial_request = json.loads(initial_request.decode('utf-8'))
    #     else:
    #         raise ValueError
    # except ValueError:
    #     err_response = json.dumps(
    #         {"response": 400, "time": time.time(),
    #          "alert": response_code_alert[400]})
    #     client_socket.send(err_response.encode('utf-8'))
    # # !!!!!!!need_authorization????
    # try:
    #     if "action" in request and
    # print('request ok')
    # if request["action"] == 'authenticate':
    #     if request['user']['account_name'] in contact_list:
    #         if request['user']['password'] == contact_list[
    #             request['user']['account_name']]:
    #             auth_response = json.dumps(
    #                 {"response": 200, "time": time.time(),
    #                  "alert": response_code_alert[200]})
    #             print('Hi Hi Hi')
    #             client_socket.send(auth_response.encode('utf-8'))
    #         else:
    #             auth_response = json.dumps(
    #                 {"response": 402, "time": time.time(),
    #                  "alert": response_code_alert[402]})
    #             client_socket.send(auth_response.encode('utf-8'))
    #     else:
    #         auth_response = json.dumps(
    #             {"response": 401, "time": time.time(),
    #              "alert": response_code_alert[401]})
    #         client_socket.send(auth_response.encode('utf-8'))
    # if request["action"] == 'quit':
    #     client_socket.close()

