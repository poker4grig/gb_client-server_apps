import datetime

from sqlalchemy import create_engine, Table, Column, String, Integer, MetaData, \
    DateTime, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker

from constants_server import SERVER_DATABASE


class ServerStorage:
    # Создание Python-сущностей таблиц
    class AllUsers:
        def __init__(self, username):
            self.name = username
            self.last_login = datetime.datetime.now()
            self.id = None

    class ActiveUsers:
        def __init__(self, user_id, ip_address, port, login_time):
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time
            self.id = None

    class LoginHistory:
        def __init__(self, name, date, ip, port):
            self.id = None
            self.name = name
            self.date_time = date
            self.ip = ip
            self.port = port

    # Класс - отображение таблицы контактов пользователей
    class UsersContacts:
        def __init__(self, user, contact):
            self.id = None
            self.user = user
            self.contact = contact

    # Отображение таблицы истории действий
    class UsersHistory:
        def __init__(self, user):
            self.id = None
            self.user = user
            self.sent = 0
            self.accepted = 0

    def __init__(self, path):
        # Подключение к БД
        print(path)
        self.database_engine = create_engine(f'sqlite:///{path}', echo=False,
                                             pool_recycle=7200,
                                             connect_args={
                                                 'check_same_thread': False})
        self.metadata = MetaData()  # Получение посредника (metadata)
        # Создание самих таблиц для БД
        users_table = Table('Users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('name', String, unique=True),
                            Column('last_login', DateTime)
                            )

        # Создаём таблицу активных пользователей
        active_users_table = Table('Active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user', ForeignKey('Users.id'),
                                          unique=True),
                                   Column('ip_address', String),
                                   Column('port', Integer),
                                   Column('login_time', DateTime)
                                   )

        # Создаём таблицу истории входов
        user_login_history = Table('Login_history', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('name', ForeignKey('Users.id')),
                                   Column('date_time', DateTime),
                                   Column('ip', String),
                                   Column('port', Integer)
                                   )

        # Создаём таблицу контактов пользователей
        contacts = Table('Contacts', self.metadata,
                         Column('id', Integer, primary_key=True),
                         Column('user', ForeignKey('Users.id')),
                         Column('contact', ForeignKey('Users.id'))
                         )

        # Создаем таблицу истории пользователей
        users_history_table = Table('History', self.metadata,
                                    Column('id', Integer, primary_key=True),
                                    Column('user', ForeignKey('Users.id')),
                                    Column('sent', Integer),
                                    Column('accepted', Integer)
                                    )

        #  миграция всех таблиц
        self.metadata.create_all(self.database_engine)
        # объединяем python-сущности таблиц и таблицы в БД
        mapper(self.AllUsers, users_table)
        mapper(self.ActiveUsers, active_users_table)
        mapper(self.LoginHistory, user_login_history)
        mapper(self.UsersContacts, contacts)
        mapper(self.UsersHistory, users_history_table)

        # создание класса сессии и получение объекта сессии
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        # при новом соединении очищаем таблицу активных пользователей
        self.session.query(self.ActiveUsers).delete()
        # подтверждаем запрос на удаление
        self.session.commit()

        # функция, записывающая в БД информацию о входе пользователя

    def user_login(self, username, ip_address, port):
        # Проверка, есть ли пользователь в таблице пользователей БД
        result = self.session.query(self.AllUsers).filter_by(name=username)
        if result.count():  # если есть, обновляем время последнего входа
            user = result.first()
            user.last_login = datetime.datetime.now()
        else:  # через экземпляр класса AllUsers передаем данные нового
            # пользователя в таблицу. Этот экземпляр отдаем в сессию
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()
            user_in_history = self.UsersHistory(user.id)
            self.session.add(user_in_history)

        # создаем запись в таблице активных пользователей о новом пользователе
        # передаем данные в таблицу через экземпляр класса ActiveUsers
        new_active_user = self.ActiveUsers(user.id, ip_address, port,
                                           datetime.datetime.now())
        self.session.add(new_active_user)
        # плюс сохраняем историю входов через экземпляр класса LoginHistory
        history = self.LoginHistory(user.id, datetime.datetime.now(),
                                    ip_address, port)
        self.session.add(history)
        # сохраняем изменения
        self.session.commit()

        # функция, фиксирующая отключение пользователя

    def user_logout(self, username):
        # получаем из БД пользователя, который отключается
        user = self.session.query(self.AllUsers).filter_by(
            name=username).first()
        # удаляем его из таблицы ActiveUsers
        self.session.query(self.ActiveUsers).filter_by(user=user.id).delete()
        self.session.commit()

    # функция, возвращающая список пользователей и время их входа
    def process_message(self, sender, recipient):
    #  Получаем ID отправителя и получателя
        sender = self.session.query(self.AllUsers).filter_by(
            name=sender).first().id
        recipient = self.session.query(self.AllUsers).filter_by(
            name=recipient).first().id
    # Запрашиваем строки из истории и увеличиваем счётчики
        sender_row = self.session.query(self.UsersHistory).filter_by\
            (user=sender).first()
        sender_row.sent += 1
        recipient_row = self.session.query(self.UsersHistory).filter_by(
            user=recipient).first()
        recipient_row.accepted += 1
        self.session.commit()

    #  Добавляем контакт для пользователя
    def add_contact(self, user, contact):
        # Получаем ID пользователей
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(
            name=contact).first()

    # Проверяем что не дубль и что контакт может существовать (полю
        # пользователь мы доверяем)
        if not contact or self.session.query(self.UsersContacts).filter_by(
                user=user.id, contact=contact.id).count():
            return

        # Создаём объект и заносим его в базу
        contact_row = self.UsersContacts(user.id, contact.id)
        self.session.add(contact_row)
        self.session.commit()

    # Удаляем контакт из БД
    def remove_contact(self, user, contact):
        user = self.session.query(self.AllUsers).filter_by(name=user).first()
        contact = self.session.query(self.AllUsers).filter_by(
            name=contact).first()
        # Проверяем что контакт может существовать (полю пользователь мы
        # доверяем)
        if not contact:
            return

        # Удаляем требуемое
        print(self.session.query(self.UsersContacts).filter(
            self.UsersContacts.user == user.id,
            self.UsersContacts.contact == contact.id
        ).delete())
        self.session.commit()

    def users_list(self):
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login
        )

        return query.all()

    # функция возвращает список активных пользователей
    def active_users_list(self):
        # соединяем таблицы с помощью join и забираем данные
        query = self.session.query(
            self.AllUsers.name,
            self.ActiveUsers.ip_address,
            self.ActiveUsers.port,
            self.ActiveUsers.login_time
        ).join(self.AllUsers)
        return query.all()

    # функция, возвращающая историю входов по пользователю или пользователям
    def login_history(self, username=None):
        # запрос истории ввода
        query = self.session.query(
            self.AllUsers.name,
            self.LoginHistory.date_time,
            self.LoginHistory.ip,
            self.LoginHistory.port
        ).join(self.AllUsers)

        if username:
            query = query.filter(self.AllUsers.name == username)
        return query.all()

    # Возвращает список контактов пользователя.
    def get_contacts(self, username):
        # Запрашивааем указанного пользователя
        user = self.session.query(self.AllUsers).filter_by(name=username).one()
        # Запрашиваем его список контактов
        query = self.session.query(self.UsersContacts, self.AllUsers.name). \
            filter_by(user=user.id). \
            join(self.AllUsers, self.UsersContacts.contact == self.AllUsers.id)
        return [contact[1] for contact in query.all()]

    # Функция возвращает количество переданных и полученных сообщений
    def message_history(self):
        query = self.session.query(
            self.AllUsers.name,
            self.AllUsers.last_login,
            self.UsersHistory.sent,
            self.UsersHistory.accepted
        ).join(self.AllUsers)
        return query.all()


if __name__ == '__main__':
    test_db = ServerStorage('server_base.db3')
    test_db.user_login('1111', '192.168.1.113', 8080)
    test_db.user_login('McG2', '192.168.1.113', 8081)
    print(test_db.users_list())
    print(test_db.active_users_list())
    test_db.user_logout('McG')
    print(test_db.login_history('re'))
    test_db.add_contact('test2', 'test1')
    test_db.add_contact('test1', 'test3')
    test_db.add_contact('test1', 'test6')
    test_db.remove_contact('test1', 'test3')
    test_db.process_message('McG2', '1111')
    print(test_db.message_history())
