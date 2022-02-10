import argparse
import time

ADDR = '127.0.0.1'
PORT = 7777

argv_parser = argparse.ArgumentParser(
    prog='command_line_client',
    description='аргументы командной строки клиента',
    epilog='автор - poker4grig'
)
argv_parser.add_argument('-a', '--addr', nargs='?', default=ADDR, help='help')
argv_parser.add_argument('-p', '--port', nargs='?', default=PORT, type=int,
                         help='help')
argv_parser.add_argument('-m', '--mode', nargs='?', default='send',
                         help='help')
argv_parser.add_argument('-u', '--user', nargs='?', default='', help='help')
ARGV_CLIENT = argv_parser.parse_args()


SIZE_OF_RECV = 4096
CURRENT_USER = ('poker4grig', "1")

PRESENCE_MSG = {
    "action": "presence",
    "time": time.time(),
    "type": "online"
}


AUTH_MSG = {
    "action": "authenticate"
}
