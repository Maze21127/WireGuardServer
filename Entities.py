from dataclasses import dataclass
from enum import Enum
import datetime


@dataclass
class DBUser:
    config_name: str
    private_key: str
    public_key: str
    ip: int


@dataclass
class TgUser:
    tg_id: int
    username: [str, None]
    first_name: [str, None]
    last_name: [str, None]
    phone: [str, None]


@dataclass
class UserSubscription:
    tg_id: int
    end_date: datetime.date
    price: int = 150
    max_configs: int = 3


@dataclass
class KeyPair:
    private_key: str
    public_key: str


@dataclass
class User:
    config_name: str
    key_pair: KeyPair
    allowed_IP: int


class ConfigNameStatus(Enum):
    LONG_STATUS = "Название слишком длинное"
    TIMEOUT = "TimeoutError"
    BLACK_LIST = "Black List"
    BAD_NAME = "Название содержит пробелы, русские символы или спецсимволы"


