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
        self.check_connection()
        self.cursor.execute(f"SELECT name FROM config WHERE tg_id = {tg_id}")
        return self.cursor.fetchall()

    def get_payment_requests(self):
        """[ONLY FOR ADMIN] Метод для получения заявок на оплату"""
        self.check_connection()
        self.cursor.execute(f"SELECT tg_id, timestamp, payment_string FROM payment_request")
        return self.cursor.fetchall()

    def get_payment_requests_for_user(self, tg_id: int):
        """Метод для получения заявок у конкретного пользователя, для предотвращения создания больше одной заявки"""
        self.check_connection()
        self.cursor.execute(f"SELECT payment_string FROM payment_request where tg_id = {tg_id}")
        return self.cursor.fetchall()

    def add_payment_request(self, tg_id: int, payment_string: str):
        """Добавляет заявку на оплату для пользователя"""
        self.check_connection()
        self.cursor.execute(f"INSERT INTO payment_request("
                            f"tg_id, timestamp, payment_string) "
                            f"VALUES("
                            f"{tg_id}, localtimestamp(0), '{payment_string}')")
        self.connection.commit()

    def accept_payment_request(self, tg_id: int):
        """[ONLY FOR ADMIN] Метод для принятия заявки на оплату"""
        self.check_connection()
        self.cursor.execute(f"DELETE FROM payment_request WHERE tg_id = {tg_id}")
        self.cursor.execute(f"SELECT subscription_end_date FROM tg_user WHERE tg_id = {tg_id}")
        date = self.cursor.fetchone()[0]
        #  Если подписки не было, добавляем 30 дней от текущего, если была, тогда к имеющейся дате.
        if date is None:
            self.cursor.execute(f"UPDATE tg_user SET subscription_end_date = "
                                f"NOW() + INTERVAL '30 DAY', active = true WHERE tg_id = {tg_id}")
        else:
            self.cursor.execute(f"UPDATE tg_user SET subscription_end_date = subscription_end_date + "
                                f"INTERVAL '30 DAY', active = true WHERE tg_id = {tg_id}")

        self.connection.commit()

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

    def get_all_active_users(self) -> list[DBUser]:
        """Метод для получения всех активных пользователей"""
        self.check_connection()
        self.cursor.execute(f"SELECT wg.publickey, wg.privatekey, active.tg_id, active.allowed_ip, active.name "
                            f"FROM wg_user wg "
                            f"LEFT JOIN"
                            f"  (SELECT c.name, c.allowed_ip, tg.active, tg.tg_id "
                            f"  FROM config c "
                            f"  LEFT JOIN tg_user tg ON c.tg_id=tg.tg_id) "
                            f"active ON active.allowed_ip=wg.allowed_ip WHERE active.active = true;")
        data = self.cursor.fetchall()
        users = []
        for user_data in data:
            user = DBUser(config_name=f"{user_data[2]}/{user_data[4]}",
                          public_key=user_data[0],
                          private_key=user_data[1],
                          ip=user_data[3])
            users.append(user)
        return users

    def add_new_user(self, tg_user: TgUser):
        self.check_connection()
        self.cursor.execute(f"INSERT INTO tg_user("
                            f"tg_id, active, username, first_name,"
                            f"last_name, phone, price)"
                            f"VALUES ({tg_user.tg_id}, {False}, '{tg_user.username}', '{tg_user.first_name}',"
                            f"'{tg_user.last_name}', '{tg_user.phone}', 150)"
                            f"ON CONFLICT(tg_id) DO NOTHING ")
        self.connection.commit()

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

    def rename_configuration_by_name(self, old_name: str, new_name: str, tg_id: int):
        self.check_connection()
        self.cursor.execute(f"UPDATE config SET name = '{new_name}' WHERE name = '{old_name}' AND tg_id = {tg_id}")
        self.connection.commit()

    def delete_config_by_name(self, name: str, tg_id: int):
        """На данный момент не используется"""
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

    def get_subscription_info_by_id(self, tg_id: int) -> UserSubscription:
        """Метод для получения стоимости подписки пользователя"""
        self.check_connection()
        self.cursor.execute(f"SELECT subscription_end_date, price, max_configs FROM tg_user WHERE tg_id = {tg_id};")
        data = self.cursor.fetchone()
        user_subscription = UserSubscription(end_date=data[0], price=data[1], max_configs=data[2])
        return user_subscription

    def get_free_ip(self) -> int:
        """Метод для получения свободного ip-адреса"""
        self.check_connection()
        self.cursor.execute(f"SELECT c.*, wg.publickey, wg.privatekey "
                            f"FROM config c "
                            f"LEFT JOIN wg_user wg ON c.allowed_ip=wg.allowed_ip;")
        ips = self.cursor.fetchall()
        using_ip = [ip[2] for ip in ips]
        for i in range(2, 254):
            if i not in using_ip and i != 3:
                return i
        return 666

    def get_keys_by_ip(self, ip: int):
        self.cursor.execute(f"SELECT privatekey, publickey FROM wg_user WHERE allowed_ip = {ip}")
        keys = self.cursor.fetchone()
        private_key = keys[0]
        public_key = keys[1]
        return KeyPair(private_key, public_key)

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
