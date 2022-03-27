from setuptools import setup, find_packages

setup(name='server_chat_pyqt_march_24',
      version='0.0.1',
      description='messenger_server_part',
      packages=find_packages(),
      author_email='my_email@yandex.ru',
      author='Grigoriev Sergey',
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
