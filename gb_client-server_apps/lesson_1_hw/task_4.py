"""
Задание 4.

Преобразовать слова «разработка», «администрирование», «protocol»,
«standard» из строкового представления в байтовое и выполнить
обратное преобразование (используя методы encode и decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
"""
dev = 'разработка'
adm = 'администрирование'
protocol = 'protocol'
standard = 'standard'

to_bytes_list = [dev, adm, protocol, standard]
to_str_list = []
print('Преобразование из строкового представления в байтовое')
for ind in range(len(to_bytes_list)):
    to_bytes_list[ind] = to_bytes_list[ind].encode('utf-8')
    to_str_list.append(to_bytes_list[ind])
    print(to_bytes_list[ind], '\n', type(to_bytes_list[ind]))
print('**********************************************************************')
print('Преобразование из байтового представления в строковое ')
for ind in range(len(to_str_list)):
    to_str_list[ind] = to_str_list[ind].decode('utf-8')
    print(to_str_list[ind], type(to_str_list[ind]))



