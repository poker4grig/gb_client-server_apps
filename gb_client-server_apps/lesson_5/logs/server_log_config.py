import logging
import sys
import os
from logging import handlers

sys.path.append('../')

LOG = logging.getLogger('app.server')

PATH = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.join(PATH, 'server.log')

TIME_ROTATE_HANDLER = logging.handlers.TimedRotatingFileHandler(PATH, when='midnight', interval=1, encoding='utf-8')
STREAM_HANDLER = logging.StreamHandler(sys.stderr)

SERVER_FORMATTER = logging.Formatter(
    f"%(asctime)-25s %(levelname)-10s %(filename)-26s %(message)s")

TIME_ROTATE_HANDLER.setFormatter(SERVER_FORMATTER)
TIME_ROTATE_HANDLER.setLevel(logging.DEBUG)
STREAM_HANDLER.setFormatter(SERVER_FORMATTER)
STREAM_HANDLER.setLevel(logging.DEBUG)

LOG.addHandler(TIME_ROTATE_HANDLER)
LOG.addHandler(STREAM_HANDLER)

LOG.setLevel(logging.DEBUG)

if __name__ == '__main__':
    LOG.critical('Критическая ошибка')
    LOG.error('Ошибка')
    LOG.debug('Отладочная информация')
    LOG.info('Информационное сообщение')
