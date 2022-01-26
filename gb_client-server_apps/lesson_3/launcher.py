"""Лаунчер"""

import subprocess

PROCESS = []

while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, x - закрыть все окна: ')
    args_server = ['python', 'server.py', '-a', '', '-p', '7777']
    args_client = ['python', 'server.py', '-a', 'localhost', '-p', '7777']
    if ACTION == 'q':
        break
    elif ACTION == 's':
        PROCESS.append(subprocess.Popen(args_server,
                                        creationflags=subprocess.CREATE_NEW_CONSOLE))
        for i in range(5):
            PROCESS.append(
                subprocess.Popen(args_client,
                                 creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ACTION == 'x':
        while PROCESS:
            VICTIM = PROCESS.pop()
            VICTIM.kill()
