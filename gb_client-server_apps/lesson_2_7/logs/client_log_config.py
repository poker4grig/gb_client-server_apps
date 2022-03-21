"""Модуль, конфигурации логгирования кода клиента."""

import logging
import os
import sys

sys.path.append('../')

LOG = logging.getLogger('app.client')

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'client.log')

FILE_HANDLER = logging.FileHandler(PATH, encoding='utf-8')
STREAM_HANDLER = logging.StreamHandler(sys.stderr)

CLIENT_FORMATTER = logging.Formatter(
    f"%(asctime)-25s %(levelname)-10s %(filename)-21s %(message)s")

FILE_HANDLER.setFormatter(CLIENT_FORMATTER)
STREAM_HANDLER.setFormatter(CLIENT_FORMATTER)
FILE_HANDLER.setLevel(logging.DEBUG)
STREAM_HANDLER.setLevel(logging.DEBUG)

LOG.addHandler(FILE_HANDLER)
LOG.addHandler(STREAM_HANDLER)
LOG.setLevel(logging.DEBUG)

if __name__ == '__main__':
    LOG.critical('Критическая ошибка')
    LOG.error('Ошибка')
    LOG.debug('Отладочная информация')
    LOG.info('Информационное сообщение')
