"""Написать функцию host_range_ping() для перебора ip-адресов из заданного
диапазона. Меняться должен только последний октет каждого адреса. По
результатам проверки должно выводиться соответствующее сообщение.
"""
import socket
from ipaddress import ip_address
from pprint import pprint
from socket import gethostbyname, inet_aton
from subprocess import Popen, PIPE
from task_1 import host_ping


def host_range_ping():
    urls = []

    while True:
        url_start = input("Введите начальное значение ip адреса: ")
        try:
            # проверяем, ip адрес в стандартном виде или в виде имени хоста
            inet_aton(url_start)
        except:
            # если ip адрес это имя хоста (типа "google.com"), то преобразуем в
            # стандартный ip адрес
            url_start = gethostbyname(url_start)
        try:
            address = ip_address(url_start)
        except ValueError:
            print("Введен некорректный ip адрес")
        else:
            break
    while True:
        url_count = input("Введите сколько адресов проверить: ")
        try:
            url_count = int(url_count)
        except ValueError:
            print("Вводить можно только число")
        else:
            break
    urls.append(address)
    for i in range(url_count - 1):
        if int(str(address).split('.')[-1]) == 255:
            break
        address += 1
        urls.append(address)

    return urls


if __name__ == '__main__':
    pprint(host_ping(host_range_ping()))
