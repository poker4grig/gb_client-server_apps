from setuptools import setup, find_packages

setup(name='client_chat_pyqt_march_25',
      version='0.0.2',
      description='messenger_client_part',
      packages=find_packages(),
      author_email='my_email@yandex.ru',
      author='Grigoriev Sergey',
      install_requires=['PyQt5', 'sqlalchemy', 'pycryptodome', 'pycryptodomex']
      )
