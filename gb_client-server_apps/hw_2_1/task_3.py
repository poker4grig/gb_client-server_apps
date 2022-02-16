"""Написать функцию host_range_ping_tab(), возможности которой основаны на
 функции из примера 2. Но в данном случае результат должен быть итоговым по
 всем ip-адресам, представленным в табличном формате (использовать модуль
 tabulate). Таблица должна состоять из двух колонок и выглядеть примерно так:
Reachable
-------------
10.0.0.1
10.0.0.2
Unreachable
-------------
10.0.0.3
10.0.0.4
"""
from ipaddress import ip_address
import socket
from tabulate import tabulate
from ipaddress import ip_address
from pprint import pprint
from socket import gethostbyname, inet_aton
from subprocess import Popen, PIPE
from task_1 import host_ping
from task_2 import host_range_ping


def host_range_ping_tab():
    urls = host_ping(host_range_ping())

    reachable = []
    unreachable = []
    for key, value in urls.items():
        if value == "Узел доступен":
            reachable.append([key])
        else:
            unreachable.append([key])

    print(tabulate(reachable, headers=["Reachable"], tablefmt="grid",
                   stralign="center"))
    print(tabulate(unreachable, headers=["Unreachable"], tablefmt="grid",
                   stralign="center"))


if __name__ == '__main__':
    host_range_ping_tab()


