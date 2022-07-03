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

    def get_user_description_by_ip(self, ip) -> str:
        self.check_connection()
        self.cursor.execute(f"SELECT description FROM customer WHERE last_ip = {ip}")
        return self.cursor.fetchone()[0]

    def get_all_users(self) -> list[DBUser]:
        self.check_connection()
        self.cursor.execute("SELECT description, publickey, privatekey, last_ip FROM customer ORDER BY id;")
        data = self.cursor.fetchall()
        users = []
        for user_data in data:
            user = DBUser(description=user_data[0],
                          public_key=user_data[1],
                          private_key=user_data[2],
                          ip=user_data[3])
            users.append(user)
        return users

    def add_user(self, user: User):
        self.check_connection()
        self.cursor.execute(f"INSERT INTO customer(description, publickey, privatekey, last_ip) VALUES"
                            f"("
                            f"'{user.description}',"
                            f"'{user.key_pair.public_key}',"
                            f"'{user.key_pair.private_key}',"
                            f"'{user.allowed_IP}');")
        self.connection.commit()

    def delete_user_by_ip(self, ip: int):
        self.check_connection()
        self.cursor.execute(f"DELETE FROM customer WHERE last_ip = {ip}")
        self.connection.commit()
        print(f"User with ip: {ip} was deleted")

    def get_free_ip(self) -> int:
        self.check_connection()
        self.cursor.execute("SELECT last_ip from customer;")
        ips = self.cursor.fetchall()
        using_ip = [ip[0] for ip in ips]
        for i in range(2, 256):
            if i not in using_ip:
                return i

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


if __name__ == "__main__":
    db = DatabaseManager()
    db.create_connection()
    users = db.get_all_users()
    for user in users:
        print(user)
    #print(db.get_free_ip())
