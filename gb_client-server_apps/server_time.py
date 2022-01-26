from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SOL_SOCKET, \
    SO_REUSEADDR, SO_BROADCAST
import time

# TCP-1
# s = socket(AF_INET, SOCK_STREAM)
#
# s.bind(('', 8888))
# s.listen(5)
#
# try:
#     while True:
#         client, addr = s.accept()
#         print('client: ', client)
#         print('addr: ', addr)
#         # print('Получен запрос на соединение от %s' % str(addr))
#         timestr = time.ctime(time.time()) + '\n'
#         client.send(timestr.encode('ascii'))
#         client.close()
# finally:
#     client.close()
# TCP-2
# s = socket(AF_INET, SOCK_STREAM)
#
# s.bind(('', 8888))
# s.listen(5)
#
# try:
#     while True:
#         client, addr = s.accept()
#         data = client.recv(1000000)
#         print('Сообщение: ', data.decode('utf-8'),
#               ', было отправлено клиентом: ', addr)
#
#         msg = 'Привет, клиент'
#         client.send(msg.encode('utf-8'))
#         client.close()
# finally:
#     client.close()
# UDP
s = socket(AF_INET, SOCK_DGRAM)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

s.bind(('', 8888))
while True:
    msg = s.recv(1024)
    print(msg.decode('utf-8'))


