import os
import re
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Transfer:
    received_gib: float = 0.0
    sent_gib: float = 0.0


@dataclass
class TransferPerUser:
    tg_id: int
    allowed_ips = []
    transfer: Transfer = Transfer()


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


def reformat_transfer_data(cursor):
    os.system("wg > info.txt")
    with open("info.txt", "r", encoding="utf-8") as info:
        data = [line.strip() for line in info.readlines()]

    data = data[5:]

    users = get_users_list(data)

    cursor.execute(f"""SELECT tg_id, allowed_ip from config order by tg_id""")
    data = cursor.fetchall()

    tg_id_dict = {tg_id[0]: [] for tg_id in data}

    for i in users:
        user = get_user(i)
        for temp in data:
            if user.allowed_ip == temp[1]:
                tg_id_dict[temp[0]].append(user.allowed_ip)


    transfer_data = []
    for key in tg_id_dict:
        temp = TransferPerUser(key)
        transfer = Transfer()

        temp_list = []
        for i in users:
            user = get_user(i)
            if user.allowed_ip in tg_id_dict[key]:
                temp_list.append(user)

        for t in temp_list:
            transfer.received_gib += t.transfer.received_gib
            transfer.sent_gib += t.transfer.sent_gib
        temp.transfer = transfer
        transfer_data.append(temp)

    cursor.execute("SELECT tg_id, received::float, sent::float from transfer")
    data = cursor.fetchall()

    for i in transfer_data:
        for j in data:
            if j[0] == i.tg_id:
                i.transfer.received_gib += j[1]
                i.transfer.sent_gib += j[2]

    for i in data:
        cursor.execute(f"""UPDATE transfer SET received = {i.transfer.received_gib}, sent = {i.transfer.sent_gib} WHERE tg_id = {i.tg_id}""")
