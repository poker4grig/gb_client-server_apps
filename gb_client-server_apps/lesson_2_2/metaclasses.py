import dis


class ServerVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        attributes = list()
        methods = list()

        for func in clsdict:
            try:
                instructions = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for inst in instructions:
                    if inst.opname == 'LOAD_GLOBAL':
                        if inst.argval not in methods:
                            methods.append(inst.argval)
                    elif inst.opname == 'LOAD_ATTR':
                        if inst.argval not in attributes:
                            attributes.append(inst.argval)
        # print(f'Методы класса Server: {methods}')
        # print(f'Атрибуты класса Server: {attributes}')

        if 'connect' in methods:
            raise TypeError('Использование метода connect недопустимо в '
                            'серверном классе')
        if not ('AF_INET' in attributes and 'SOCK_STREAM' in attributes):
            raise TypeError('Некорректная инициализация сокета.')
        super().__init__(clsname, bases, clsdict)


class ClientVerifier(type):
    def __init__(self, clsname, bases, clsdict):
        methods = list()
        attributes = list()
        for func in clsdict:
            try:
                instructions = dis.get_instructions(clsdict[func])
            except TypeError:
                pass
            else:
                for inst in instructions:
                    if inst.opname == 'LOAD_GLOBAL':
                        if inst.argval not in methods:
                            methods.append(inst.argval)
                    elif inst.opname == 'LOAD_ATTR':
                        if inst.argval not in attributes:
                            attributes.append(inst.argval)
        # print(f'Методы класса Client: {methods}')
        # print(f'Атрибуты класса Client: {attributes}')
        if any(i for i in ('accept', 'listen') if i in methods):
            raise TypeError(
                'В классе обнаружено использование запрещённого метода')
        super().__init__(clsname, bases, clsdict)
        if not ('AF_INET' in attributes and 'SOCK_STREAM' in attributes):
            raise TypeError(
                'Отсутствуют атрибуты AF_INET и SOCK_STREAM при создании '
                'сокета ')
