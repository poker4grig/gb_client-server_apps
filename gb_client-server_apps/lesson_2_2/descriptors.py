import logging
from socket import inet_aton, gethostbyname
from ipaddress import ip_address
LOG = logging.getLogger('app.server')


class Port:
    def __set__(self, instance, value):
        if not 1023 < value < 65536:
            LOG.critical(f'Попытка запуска сервера с указанием неподходящего '
                         f'порта {value}. Допустимы адреса с 1024 до 65535.')
            exit(1)
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name


class Host:
    def __set__(self, instance, value):
        try:
            ip_address(value)
        except ValueError:
            print("Значение ip адреса не должно быть именем домена или пустой "
                  "строкой")
            exit(1)

        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
