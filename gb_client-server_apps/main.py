# import argparse
#
# argv_parser = argparse.ArgumentParser(
#     prog='command_line_arguments',
#     description='аргументы командной строки',
#     epilog='автор - poker4grig'
# )
# argv_parser.add_argument('-a', '--addr', nargs='?', default='', help='help')
# argv_parser.add_argument('-p', '--port', nargs='?', default=7777)
# agrs = argv_parser.parse_args()
# print(agrs.addr)
# print(agrs.port)


# import selectors
# import sys
# import pprint
# import time
# from collections import namedtuple
#
# n_t = namedtuple('Greating', 'id first second by_by')
# print(dir(n_t))
# N_T = n_t(id=1, first='first', second='second', by_by='ty')
# print(N_T.__dict__)


# print(sys.platform)
# print(selectors.DefaultSelector())
# response_code_alert = {
#     100: "basic notification ", 101: "important notice",
#     200: 'OK', 201: "object created", 202: "accepted",
#     400: "wrong request/JSON object",
#     401: "not authorized", 402: "wrong login/password",
#     403: "user forbidden",
#     404: "user/chat is missing from the server",
#     409: "there is already a connection with this login",
#     410: "destination exists but is not available (offline)",
#     500: "server error"
# }

# bs = b'Python'
#
# # Отдельный тип - bytearray - изменяемая строка байтов
# ba = bytearray(bs)
#
# ba.append(2)
# a = ba.decode('utf-8')
# print(a)
