from dataclasses import dataclass
import re
from datetime import datetime


@dataclass
class Transfer:
    received_gib: float = 0.0
    sent_gib: float = 0.0


@dataclass
class UserInfo:
    peer: str
    endpoint: str
    allowed_ip: int
    latest_handshake: str
    transfer: Transfer


def get_gb_transfer(transfer_string: list, index: int) -> float:
    if transfer_string[index] == "KiB":
        transfer_data = round(float(transfer_string[index - 1]) / 1000**2, 3)
    elif transfer_string[index] == "MiB":
        transfer_data = round(float(transfer_string[index - 1]) / 1000 ** 1, 3)
    elif transfer_string[index] == "GiB":
        transfer_data = float(transfer_string[index - 1])
    else:
        transfer_data = 0.0
    return transfer_data


def get_transfer(transfer_string: str) -> Transfer:
    divided_transfer_string = transfer_string.split()
    received_gib = get_gb_transfer(divided_transfer_string, 2)
    sent_gib = get_gb_transfer(divided_transfer_string, 5)
    return Transfer(received_gib, sent_gib)


def get_seconds(time_list: list[str]):
    time_list = list(map(int, time_list))
    time = 0
    if len(time_list) == 3:
        time = time_list[0] * 60 + time_list[1] * 60 + time_list[2]
    elif len(time_list) == 2:
        time = time_list[0] * 60 + time_list[1]
    elif len(time_list) == 1:
        time = time_list[1]
    return time


def get_last_handshake_time(seconds: int):
    now = datetime.timestamp(datetime.now())
    return datetime.fromtimestamp(now - seconds).strftime("%y.%m.%d %H:%M:%S")


def get_user(file_string: list) -> UserInfo:
    peer = file_string[0].split(":")[1].strip()
    if len(file_string) == 2:
        allowed_ip = int(re.search(r'.\d/', file_string[1].split(":")[1].strip()).group(0)[1:-1])
        return UserInfo(peer=peer, endpoint="", allowed_ip=allowed_ip, latest_handshake="", transfer=Transfer())
    elif len(file_string) == 5:
        endpoint = file_string[1].split(":")[1].strip()
        allowed_ip = int(re.search(r'.\d/', file_string[2].split(":")[1].strip()).group(0)[1:-1])
        time = re.findall(r"\d+", file_string[3].split(":")[1].strip())
        time = get_last_handshake_time(get_seconds(time))
        transfer = get_transfer(file_string[4])
        return UserInfo(peer, endpoint, allowed_ip, time, transfer)


def get_users_list(user_list: list):
    index = 0
    users = []
    while True:
        temp = []
        while True:
            try:
                if user_list[index] == "":
                    index += 1
                    break
            except IndexError:
                return users
            temp.append(user_list[index])
            index += 1
        users.append(temp)


with open("info.txt", "r", encoding="utf-8") as info:
    data = [line.strip() for line in info.readlines()]

data = data[5:]


users = get_users_list(data)

for i in users:
    user = get_user(i)
    print(user)

