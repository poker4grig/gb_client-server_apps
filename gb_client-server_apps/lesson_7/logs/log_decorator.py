import sys
import logging
import traceback
import inspect

if 'client.' in sys.argv[0] or 'client_' in sys.argv[0]:
    LOG = logging.getLogger('app.client')
else:
    LOG = logging.getLogger('app.server')


def log_func(logging_func):
    def wrapper(*args, **kwargs):
        result = logging_func(*args, **kwargs)
        LOG.debug(
            f'Была вызвана функция {logging_func.__name__} c параметрами {args}, {kwargs}. '
            f'Вызов из модуля {logging_func.__module__}. Вызов из'
            f' функции {traceback.format_stack()[0].strip().split()[-1]}.'
            f'Вызов из функции {inspect.stack()[1][3]}', stacklevel=2)
        return result

    return wrapper

