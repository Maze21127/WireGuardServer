class UserAlreadyExists(Exception):
    """Исключение, если пользователь уже существует"""


class UserNotExists(Exception):
    """Исключение, если пользователь уже существует"""


class NoDatabaseConnection(Exception):
    """Исключение при попытке взаимодействия с базой данных, к которой не установленно подключение"""


class NoCursor(Exception):
    """Исключение при попытке взаимодействия с неинициализированным курсором"""
