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

    def get_configs_list_for_user(self, tg_id: int):
        configs = self._database.get_configs_list_for_user(tg_id)
        return [config[0] for config in configs]

    def create_user_config_by_name(self, name: str, tg_id: int) -> (str, str):
        self._user = self._database.get_user_by_name(name, tg_id)
        return self._create_user_config()

    def delete_user_config_by_name(self, name: str, tg_id: int):
        self._database.delete_config_by_name(name, tg_id)
        self._reformat_config_file()
        self.restart_wireguard()

    def is_user_active(self, tg_id: int):
        status = self._database.get_user_active(tg_id)
        return status

    def get_price_by_id(self, tg_id: int):
        return self._database.get_price_by_id(tg_id)

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

    def _reformat_config_file(self):
        self._create_config_file()
        for user in self._database.get_all_users():
            key_pair = KeyPair(user.private_key, user.public_key)
            self._user = User(user.config_name, key_pair, user.ip)
            self._add_user_to_config()

    def create_new_config(self, config_name: str, tg_id: int):
        ip = self._database.get_free_ip()
        if ip == 666:
            raise NoFreeIpAddress("Ошибка, нет свободных адресов")

        self._user = User(config_name, get_user_keypair(), ip)
        self._database.create_new_config(self._user, tg_id)
        self._reformat_config_file()
        self.restart_wireguard()
        return self.create_user_config_by_name(config_name, tg_id)

    def _create_user_config(self) -> (str, str):
        config = f'configs/{self._user.config_name}.conf'

        f = open(config, "w")
        f.close()

        with open(config, "a") as file:
            file.write("[Interface]\n")
            file.write(f"PrivateKey = {self._user.key_pair.private_key}\n")
            file.write(f"Address = 10.0.0.{self._user.allowed_IP}/32\n")
            file.write("DNS = 8.8.8.8\n\n")
            file.write("[Peer]\n")
            file.write(f"PublicKey = {WG_PUBLIC_KEY}\n")
            file.write(f"Endpoint = {WG_ENDPOINT}\n")
            file.write("AllowedIPs = 0.0.0.0/0\n")
            file.write("PersistentKeepalive = 20\n")

        os.system(f"qrencode -t png -o {config}_qr.png -r {config}")
        qr_code = f'{config}_qr.png'
        return config, qr_code

    @staticmethod
    def delete_user_config(config_name: str):
        file = f'configs/{config_name}.conf'
        try:
            os.remove(file)
        except FileExistsError:
            return

    def _add_user_to_config(self):
        with open("../wg0.conf", "a") as file:
            file.write("\n[Peer]\n")
            file.write(f"# {self._user.config_name}\n")
            file.write(f"PublicKey = {self._user.key_pair.public_key}\n")
            file.write(f"AllowedIPs = 10.0.0.{self._user.allowed_IP}/32\n")

    def restart_wireguard(self):
        self._update_transfer()
        os.system("systemctl restart wg-quick@wg0")

    def _update_transfer(self):
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
