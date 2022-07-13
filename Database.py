import psycopg2

from exceptions import *
from settings import *
from Entities import *


class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def create_connection(self):
        try:
            self.connection = psycopg2.connect(
                host=DB_HOST,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_NAME
            )
            self.cursor = self.connection.cursor()
        except Exception as ex:
            print("[INFO] Error while working with PostgreSQL", ex)

    def get_configs_list_for_user(self, tg_id: int):
        self.cursor.execute(f"""SELECT name FROM config WHERE tg_id = {tg_id}""")
        return self.cursor.fetchall()

    def get_user_description_by_ip(self, ip) -> str:
        self.check_connection()
        self.cursor.execute(f"SELECT description FROM customer WHERE last_ip = {ip}")
        return self.cursor.fetchone()[0]

    def get_all_users(self) -> list[DBUser]:
        self.check_connection()
        self.cursor.execute(f"SELECT c.*, wg.publickey, wg.privatekey "
                            f"FROM config c "
                            f"LEFT JOIN wg_user wg ON c.allowed_ip=wg.allowed_ip;")
        data = self.cursor.fetchall()
        users = []
        for user_data in data:
            user = DBUser(config_name=f"{user_data[3]}/{user_data[1]}",
                          public_key=user_data[4],
                          private_key=user_data[5],
                          ip=user_data[2])
            users.append(user)
        return users

    def create_new_config(self, user: User, tg_id: int):
        self.check_connection()
        self.cursor.execute(f"INSERT INTO wg_user(publickey, privatekey, allowed_ip) VALUES("
                            f"'{user.key_pair.public_key}',"
                            f"'{user.key_pair.private_key}',"
                            f"{user.allowed_IP})")
        self.cursor.execute(f"INSERT INTO config(name, allowed_ip, tg_id) VALUES("
                            f"'{user.config_name}',"
                            f"'{user.allowed_IP}',"
                            f"'{tg_id}')")
        self.connection.commit()
        print(f"Config {user.config_name}/{tg_id} создан")

    def delete_config_by_name(self, name: str, tg_id: int):
        self.check_connection()
        self.cursor.execute(f"SELECT allowed_ip FROM config WHERE name = '{name}' AND tg_id = {tg_id}")
        ip = self.cursor.fetchone()[0]
        self.cursor.execute(f"DELETE FROM config WHERE name = '{name}' AND tg_id = {tg_id}")
        self.cursor.execute(f"DELETE FROM wg_user WHERE allowed_ip = {ip}")
        self.connection.commit()
        print(f"Config {name}/{tg_id} удален")

    def get_user_by_name(self, name: str, tg_id: int):
        self.check_connection()
        self.cursor.execute(f"SELECT allowed_ip FROM config WHERE tg_id = {tg_id} AND name = '{name}'")
        ip = self.cursor.fetchone()[0]
        self.cursor.execute(f"SELECT publickey, privatekey FROM wg_user WHERE allowed_ip = {ip}")
        data = self.cursor.fetchone()
        return User(name, KeyPair(public_key=data[0], private_key=data[1]), ip)

    def get_user_active(self, tg_id) -> bool:
        """Метод для проверки состония подписки пользователя"""
        self.check_connection()
        self.cursor.execute(f"SELECT active FROM tg_user WHERE tg_id = {tg_id}")
        return self.cursor.fetchone()[0]

    def get_price_by_id(self, tg_id: int) -> int:
        """Метод для получения стоимости подписки пользователя"""
        self.check_connection()
        self.cursor.execute(f"SELECT price FROM tg_user WHERE tg_id = {tg_id}")
        return self.cursor.fetchone()[0]

    def get_free_ip(self) -> int:
        """Метод для получения свободного ip-адреса"""
        self.check_connection()
        self.cursor.execute("SELECT allowed_ip from wg_user;")
        ips = self.cursor.fetchall()
        using_ip = [ip[0] for ip in ips]
        for i in range(2, 256):
            if i not in using_ip:
                return i
        return 666

    def check_connection(self):
        if self.connection is None:
            raise NoDatabaseConnection("No PostgreSQL connection")
        if self.cursor is None:
            raise NoCursor("No PostgreSQL cursor")

    def __del__(self):
        if self.connection is not None:
            self.connection.close()
            self.cursor.close()
            print("[INFO] PostgreSQL connection closed")
