"""
Задание 2.

Каждое из слов «class», «function», «method» записать в байтовом формате
без преобразования в последовательность кодов
не используя!!! методы encode и decode)
и определить тип, содержимое и длину соответствующих переменных.

Подсказки:
--- b'class' - используйте маркировку b''
--- используйте списки и циклы, не дублируйте функции
"""
_class = 'class'
_function = 'function'
_method = 'method'

change_list = [_class, _function, _method]

for item in change_list:
    item = bytes(item, encoding='UTF-8')
    print(type(item), item, len(item))
