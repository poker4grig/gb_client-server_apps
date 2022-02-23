import datetime

from sqlalchemy import create_engine, Table, Column, String, Integer, MetaData, \
    DateTime, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker

from constants_server import SERVER_DATABASE


class ServerStorage:
    # Создание Python-сущностей таблиц
    class AllUsers:
        def __init__(self, username):
            self.id = None
            self.username = username
            self.last_login = datetime.datetime.now()

    class ActiveUser:
        def __init__(self, user_id, ip_address, port, login_time):
            self.id = None
            self.user = user_id
            self.ip_address = ip_address
            self.port = port
            self.login_time = login_time

    class LoginHistory:
        def __init__(self, name, date, ip, port):
            self.id = None
            self.name = name
            self.date_time = date
            self.ip = ip
            self.port = port

    def __init__(self):
        # Подключение к БД
        self.database_engine = create_engine(SERVER_DATABASE, echo=False,
                                             pool_recycle=7200)
        self.metadata = MetaData()  # Получение посредника (metadata)
        # Создание самих таблиц для БД
        users_table = Table('Users', self.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('username', String, unique=True),
                            Column('last_login', DateTime)
                            )

        active_users_table = Table('Active_users', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('user', ForeignKey('Users.id'),
                                          unique=True),
                                   Column('ip_address', String),
                                   Column('port', Integer),
                                   Column('login_time', DateTime)
                                   )

        user_login_history = Table('Login_history', self.metadata,
                                   Column('id', Integer, primary_key=True),
                                   Column('name', ForeignKey('Users.id')),
                                   Column('date_time', DateTime),
                                   Column('ip', String),
                                   Column('port', Integer)
                                   )
        #  миграция всех таблиц
        self.metadata.create_all(self.database_engine)
        # объединяем python-сущности таблиц и таблицы в БД
        mapper(self.AllUsers, users_table)
        mapper(self.ActiveUser, active_users_table)
        mapper(self.LoginHistory, user_login_history)

        # создание класса сессии и получение объекта сессии
        Session = sessionmaker(bind=self.database_engine)
        self.session = Session()

        # при новом соединении очищаем таблицу активных пользователей
        self.session.query(self.ActiveUser).delete()
        # подтверждаем запрос на удаление
        self.session.commit()

        # функция, записывающая в БД информацию о входе пользователя

    def user_login(self, username, ip_address, port):
        print(username, ip_address, port)
        # Проверка, есть ли пользователь в таблице пользователей БД
        result = self.session.query(self.AllUsers).filter_by(name=username)
        print("это переменная запроса result - ", type(result))
        if result.count():  # если есть, обновляем время последнего входа
            user = result.first()
            user.last_login = datetime.datetime.now()
        else:  # через экземпляр класса AllUsers передаем данные нового
            # пользователя в таблицу. Этот экземпляр отдаем в сессию
            user = self.AllUsers(username)
            self.session.add(user)
            self.session.commit()

        # создаем запись в таблице активных пользователей о новом пользователе
        # передаем данные в таблицу через экземпляр класса ActiveUser
        new_active_user = self.ActiveUser(user.id, ip_address, port,
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
            username=username).first()
        # удаляем его из таблицы ActiveUsers
        self.session.query(self.ActiveUser).filter_by(user=user.id).delete()
        self.session.commit()

    # функция, возвращающая список пользователей и время их входа
    def users_list(self):
        query = self.session.query(
            self.AllUsers.username,
            self.LoginHistory.date,
            self.LoginHistory.ip,
            self.LoginHistory.port).join(self.AllUsers)

        return query.all()

    # функция возвращает список активных пользователей
    def active_users_list(self):
        # соединяем таблицы с помощью join и забираем данные
        query = self.session.query(
            self.ActiveUser.user,
            self.ActiveUser.ip_address,
            self.ActiveUser.port,
            self.ActiveUser.login_time
        ).join(self.AllUsers)
        return query.all()

    # функция, возвращающая историю входов по пользователю или пользователям
    def login_history(self, username=None):
        # запрос истории ввода
        query = self.session.query(
            self.AllUsers.username,
            self.LoginHistory.date_time,
            self.LoginHistory.ip,
            self.LoginHistory.port
        ).join(self.AllUsers)

        if username:
            query = query.filter(self.AllUsers.username == username)
        return query.all()


if __name__ == '__main__':
    test_db = ServerStorage()
    # подключаем пользователей
    test_db.user_login('client_1', '127.0.0.1', 7777)
    test_db.user_login('client_2', '127.0.0.1', 7777)
    # выводим список активных пользователей
    print(test_db.active_users_list())
    # отключаем пользователя
    test_db.user_logout('client_1')
    # еще раз выводим список активных пользователей
    print(test_db.active_users_list())
    # запрос истории входов по пользователю
    test_db.login_history('client_1')
    # еще раз выводим список активных пользователей
