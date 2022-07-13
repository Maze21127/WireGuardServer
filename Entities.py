from dataclasses import dataclass


@dataclass
class DBUser:
    config_name: str
    private_key: str
    public_key: str
    ip: int


@dataclass
class KeyPair:
    private_key: str
    public_key: str


@dataclass
class User:
    config_name: str
    key_pair: KeyPair
    allowed_IP: int
