"""
Задание 5.

Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.

Подсказки:
--- используйте модуль chardet, иначе задание не засчитается!!!
"""
import chardet
import subprocess

args = ['ping']
SITES = ['yandex.ru', 'google.com']

for site in SITES:
    args.append(site)
    subproc_ping = subprocess.Popen(args, stdout=subprocess.PIPE)
    print(f'*** пинг сайта {site} ***')
    for line in subproc_ping.stdout:
        result = chardet.detect(line)
        read_line = line.decode(result['encoding'])
        print(read_line)
    args.pop()

