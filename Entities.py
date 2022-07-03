from dataclasses import dataclass


@dataclass
class DBUser:
    description: str
    private_key: str
    public_key: str
    ip: int


@dataclass
class KeyPair:
    private_key: str
    public_key: str


@dataclass
class User:
    description: str
    key_pair: KeyPair
    allowed_IP: int
