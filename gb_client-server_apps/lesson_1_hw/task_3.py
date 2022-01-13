"""
Задание 3.

Определить, какие из слов «attribute», «класс», «функция», «type»
невозможно записать в байтовом типе с помощью маркировки b'' (без encode decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
--- обязательно!!! усложните задачу, "отловив" и обработав исключение,
придумайте как это сделать
"""
class NotAscii(Exception):
    def __str__(self):
        return 'невозможно записать в байтовом типе с помощью маркировки b ' \
               'слово: '


attr = 'attribute'
_class = 'класс'
func = 'функция'
_type = 'type'
check_list = [attr, _class, func, _type]
for item in check_list:
    try:
        if not item.isascii():
            raise NotAscii
        item = bytes(item, encoding='utf-8')
    except NotAscii as e:
        print(e, item)
    else:
        print(item)


