from Database import DatabaseManager
from exceptions import *
import os
import time
from settings import WG_PUBLIC_KEY, WG_ENDPOINT, WG_PRIVATE_KEY
from Entities import *
from wg_info import reformat_transfer_data


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
        description = self._database.get_user_description_by_ip(ip)
        self._database.delete_user_by_ip(ip)
        self._delete_user_config(description)
        self._reformat_config_file()

    @staticmethod
    def _create_config_file():
        """Delete old file and create new with header"""
        os.remove("../wg0.conf")
        with open("../wg0.conf", "a") as file:
            file.write("[Interface]\n")
            file.write(f"PrivateKey = {WG_PRIVATE_KEY}\n")
            file.write("Address = 10.0.0.1/24\n")
            file.write("ListenPort = 51830\n")
            file.write("PostUp = iptables -A FORWARD -i %i -j ACCEPT; iptables -t nat -A POSTROUTING -o ens3 -j "
                       "MASQUERADE\n")
            file.write("PostDown = iptables -D FORWARD -i %i -j ACCEPT; iptables -t nat -D POSTROUTING -o ens3 -j "
                       "MASQUERADE\n\n")

    def create_config_file_by_ip(self, ip: int):
        self._user = self._database.get_user_by_ip(ip)
        self._create_user_config()
        print(f"[INFO] config file for user with ip {ip} created successfully")

    def _reformat_config_file(self):
        self._create_config_file()
        for user in self._database.get_all_users():
            key_pair = KeyPair(user.private_key, user.public_key)
            self._user = User(user.description, key_pair, user.ip)
            self._add_user_to_config()

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

    @staticmethod
    def _delete_user_config(description: str):
        file = f'configs/{description}.conf'
        print(file)
        if not os.path.exists(file):
            print("User not already exists")
            raise FileExistsError("File not exists")
        os.remove(file)

    def _add_user_to_config(self):
        with open("../wg0.conf", "a") as file:
            file.write("\n[Peer]\n")
            file.write(f"# {self._user.description}\n")
            file.write(f"PublicKey = {self._user.key_pair.public_key}\n")
            file.write(f"AllowedIPs = 10.0.0.{self._user.allowed_IP}/32\n")

    def update_transfer(self):
        reformat_transfer_data(self._database.cursor)
        self._database.connection.commit()

    def create_database_connection(self):
        try:
            self._database.create_connection()
        except NoDatabaseConnection as ex:
            print("[INFO] ", ex)
            return
        except NoCursor as ex:
            print("[INFO] ", ex)
            return
