"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт,
осуществляющий выборку определенных данных из файлов info_1.txt, info_2.txt,
info_3.txt и формирующий новый «отчетный» файл в формате CSV.

Для этого:

Создать функцию get_data(), в которой в цикле осуществляется перебор файлов
с данными, их открытие и считывание данных. В этой функции из считанных данных
необходимо с помощью регулярных выражений или другого инструмента извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
Значения каждого параметра поместить в соответствующий список. Должно
получиться четыре списка — например, os_prod_list, os_name_list,
os_code_list, os_type_list. В этой же функции создать главный список
для хранения данных отчета — например, main_data — и поместить в него
названия столбцов отчета в виде списка: «Изготовитель системы»,
«Название ОС», «Код продукта», «Тип системы». Значения для этих
столбцов также оформить в виде списка и поместить в файл main_data
(также для каждого файла);

Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл.
В этой функции реализовать получение данных через вызов функции get_data(),
а также сохранение подготовленных данных в соответствующий CSV-файл;

Пример того, что должно получиться:

Изготовитель системы,Название ОС,Код продукта,Тип системы

1,LENOVO,Windows 7,00971-OEM-1982661-00231,x64-based

2,ACER,Windows 10,00971-OEM-1982661-00231,x64-based

3,DELL,Windows 8.1,00971-OEM-1982661-00231,x86-based

Обязательно проверьте, что у вас получается примерно то же самое.

ПРОШУ ВАС НЕ УДАЛЯТЬ СЛУЖЕБНЫЕ ФАЙЛЫ TXT И ИТОГОВЫЙ ФАЙЛ CSV!!!
"""
import re
import csv

info_files = ['info_1.txt', 'info_2.txt', 'info_3.txt']


def get_data():
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    header = ['№', 'Изготовитель системы', 'Название ОС', 'Код продукта',
              'Тип системы']
    order_num = [1]
    main_data = []

    for file in info_files:
        with open(file, 'r', encoding='utf-8') as f:
            search_re = f.read()
            os_prod_list.append(
                re.search(r"Изготовитель системы: \s+ (\S+)",
                          search_re).groups()[0])
            os_name_list.append(
                re.search(r'Название ОС:\s+(\w+\s+\w+\s*\d+.?\d?\s*\w+)',
                          search_re).groups()[0])
            os_code_list.append(re.search(r'Код продукта:\s+(\d+-\w+-\w+-\w+)',
                                          search_re).groups()[0])
            os_type_list.append(
                re.search(r'Тип системы:\s+(\w+-\w+\s*\w+)',
                          search_re).groups()[0])
            order_num.append(order_num[-1] + 1)

    main_data.append(header)
    for ind in range(len(os_type_list)):
        main_data.append([])
        main_data[ind + 1].append((order_num[ind]))
        main_data[ind + 1].append(os_prod_list[ind])
        main_data[ind + 1].append(os_name_list[ind])
        main_data[ind + 1].append(os_code_list[ind])
        main_data[ind + 1].append(os_type_list[ind])
    return main_data


def write_to_csv(to_crv_file):
    with open('report.csv', 'w', encoding='utf-8') as file:
        f_n_writer = csv.writer(file)
        f_n_writer.writerows(to_crv_file)


write_to_csv(get_data())
