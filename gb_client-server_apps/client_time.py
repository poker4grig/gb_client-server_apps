from socket import socket, AF_INET, SOCK_STREAM, SOCK_DGRAM, SOL_SOCKET, \
    SO_REUSEADDR, SO_BROADCAST
# TCP
# try:
#     while True:
#         client_socket = socket(AF_INET, SOCK_STREAM)
#
#         client_socket.connect(('localhost', 8888))
#
#         # msg = 'Привет, сервер'
#         client_socket.send('Привет, сервер'.encode('utf-8'))
#         data = client_socket.recv(1000000)
#         client_socket.close()
#         print('Сообщение от сервера: ', data.decode('utf-8'), ', длиной ', len(data), ' байт')
#
# finally:
#     client_socket.close()

# UDP
s = socket(AF_INET, SOCK_DGRAM)
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
while True:
    s.sendto('Запрос на соединение!'.encode('utf-8'), ('localhost', 8888))


