import argparse
import logging
import sys
from PyQt5.QtWidgets import QApplication

from errors import ServerError
from logs.log_decorator import log_func
from client.constants_client import PORT, ADDR
from client.database import ClientDatabase
from client.transport import ClientTransport
from client.main_window import ClientMainWindow
from client.start_dialog import UserNameDialog

LOG = logging.getLogger("app.client")


@log_func
def client_argv():
    """Парсер аргументов командной строки для клиента"""
    argv_parser = argparse.ArgumentParser(
        prog='command_line_client',
        description='аргументы командной строки клиента',
        epilog='автор - Григорьев Сергей'
    )
    argv_parser.add_argument('addr', default=ADDR, nargs='?', help='help')
    argv_parser.add_argument('port', default=PORT, type=int, nargs='?',
                             help='help')
    argv_parser.add_argument('-n', '--name', default=None, nargs='?',
                             help='help')
    namespace = argv_parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    if not 1023 < server_port < 65536:
        LOG.critical(
            f'Попытка запуска клиента с неподходящим номером порта: '
            f'{server_port}. Допустимы адреса с 1024 до 65535. '
            f'Клиент завершается.')
        exit(1)
    return server_address, server_port, client_name


if __name__ == '__main__':
    server_address, server_port, client_name = client_argv()

    client_app = QApplication(sys.argv)

    if not client_name:
        start_dialog = UserNameDialog()
        client_app.exec_()
        if start_dialog.ok_pressed:
            client_name = start_dialog.client_name.text()
            del start_dialog
        else:
            exit(0)
    LOG.info(
        f'Запущен клиент с параметрами: адрес сервера: {server_address} , '
        f'порт: {server_port}, имя пользователя: {client_name}')

    database = ClientDatabase(client_name)

    # Инициализация сокета и приветственное сообщение
    try:
        transport = ClientTransport(server_port, server_address, database,
                                    client_name)
    except ServerError as error:
        print(error.text)
        exit(1)
    transport.setDaemon(True)
    transport.start()

    #GUI
    main_window = ClientMainWindow(database, transport)
    main_window.make_connection(transport)
    main_window.setWindowTitle(f'Чат Программа alpha release - {client_name}')
    client_app.exec_()

    # Если графическая оболочка закрылась, закрываем транспорт
    transport.transport_shutdown()
    transport.join()
