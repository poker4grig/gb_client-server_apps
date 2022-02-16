"""Написать функцию host_ping(), в которой с помощью утилиты ping будет
проверяться доступность сетевых узлов. Аргументом функции является список, в
котором каждый сетевой узел должен быть представлен именем хоста или
ip-адресом. В функции необходимо перебирать ip-адреса и проверять их
доступность с выводом соответствующего сообщения («Узел доступен»,
«Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с
помощью функции ip_address().
"""
from ipaddress import ip_address
from subprocess import Popen, PIPE
from socket import gethostbyname
from pprint import pprint


def host_ping(url_lst):
    result = {}
    for url in url_lst:
        try:
            address = ip_address(url)
        except ValueError:
            address = gethostbyname(url)
        with Popen(f"ping {address} -w 500 -n 1", stdout=PIPE) as proc:
            proc.wait()
        if proc.returncode == 0:
            result[address] = "Узел доступен"
        else:
            result[address] = "Узел недоступен"
    return result


urls = ["google.com", "python.org", "216.239.32.21", "23.227.38.32",
        "74.125.22.132", "209.99.64.71", "192.0.78.13", "192.0.78.12",
        "208.91.197.26", "79.127.127.68", "5.144.133.146", "178.248.232.65",
        "216.239.34.21", "216.239.38.21", "216.239.36.21", "208.91.197.25",
        "141.8.225.31", "208.93.0.150", "95.213.255.23", "38.74.1.50",
        "208.91.197.27", "38.74.1.45"]

if __name__ == '__main__':
    pprint(host_ping(urls))

