from Database import DatabaseManager
from exceptions import *
import os
import time
from settings import WG_PUBLIC_KEY, WG_ENDPOINT
from Entities import *


def get_user_keypair() -> KeyPair:
    timestamp = int(time.time())
    os.system(f"wg genkey > temp_key{timestamp}")
    with open(f"temp_key{timestamp}", "r") as file:
        private_key = file.read().strip()

    os.system(f"wg pubkey < temp_key{timestamp} > temp_pubkey{timestamp}")
    with open(f"temp_pubkey{timestamp}", "r") as file:
        public_key = file.read().strip()

    os.remove(f"temp_key{timestamp}")
    os.remove(f"temp_pubkey{timestamp}")

    return KeyPair(private_key, public_key)


class UserManager:
    def __init__(self):
        self._database = DatabaseManager()
        self._user = None

    def delete_user_by_ip(self, ip: int):
        self._database.delete_user_by_ip(ip)

    def create_user(self, description: str):
        self._user = User(description, get_user_keypair(), self._database.get_free_ip())
        try:
            self._create_user_config()
            self._add_user_to_config()
            self._database.add_user(self._user)
        except FileExistsError:
            return

    def _create_user_config(self):
        file = f'configs/{self._user.description}.conf'

        if os.path.exists(file):
            print("File already exists")
            raise FileExistsError("File already exists")

        with open(file, "a") as file:
            file.write("[Interface]\n")
            file.write(f"PrivateKey = {self._user.key_pair.private_key}\n")
            file.write(f"Address = 10.0.0.{self._user.allowed_IP}/32\n")
            file.write("DNS = 8.8.8.8\n\n")
            file.write("[Peer]\n")
            file.write(f"PublicKey = {WG_PUBLIC_KEY}\n")
            file.write(f"Endpoint = {WG_ENDPOINT}\n")
            file.write("AllowedIPs = 0.0.0.0/0\n")
            file.write("PersistentKeepalive = 20\n")

    def _add_user_to_config(self):
        with open("wg0.conf", "a") as file:
            file.write("\n[Peer]\n")
            file.write(f"# {self._user.description}\n")
            file.write(f"PublicKey = {self._user.key_pair.public_key}\n")
            file.write(f"AllowedIPs = 10.0.0.{self._user.allowed_IP}/32\n")

    def create_database_connection(self):
        try:
            self._database.create_connection()
        except NoDatabaseConnection as ex:
            print("[INFO] ", ex)
            return
        except NoCursor as ex:
            print("[INFO] ", ex)
            return


if __name__ == "__main__":
    manager = UserManager()
    manager.create_database_connection()
    #manager.create_user("Test123456")
    manager.delete_user_by_ip(11)
    manager.delete_user_by_ip(12)
    for usr in manager._database.get_all_users():
        print(usr)
