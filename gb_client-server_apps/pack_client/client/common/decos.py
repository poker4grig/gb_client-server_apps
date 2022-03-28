"""Модуль, содержащий функции-декораторы приложения."""

import socket
import logging
import sys

sys.path.append('../client/')

# метод определения модуля, источника запуска.
if sys.argv[0].find('client') == -1:
    # если не клиент, то сервер!
    logger = logging.getLogger('app.server')
else:
    # иначе сервер
    logger = logging.getLogger('app.client')


def log(func_to_log):
    """Декоратор, выполняющий логирование вызовов функций.

    Сохраняет события типа debug, содержащие информацию об имени вызываемой
    функции, параметры с которыми вызывается функция, и модуль, вызывающий
    функцию.
    """

    def log_saver(*args, **kwargs):
        logger.debug(
            f'Была вызвана функция {func_to_log.__name__} c параметрами '
            f'{args}, {kwargs}. Вызов из модуля {func_to_log.__module__}')
        ret = func_to_log(*args, **kwargs)
        return ret

    return log_saver



