from os import getenv
from dotenv import load_dotenv


load_dotenv('.env')

# IP-Адресс базы данных PostgreSQL
DB_HOST = getenv('DB_HOST')
# Логин пользователя базы данных
DB_USER = getenv("DB_USER")
# Пароль пользователя базы данных
DB_PASSWORD = getenv("DB_PASSWORD")
# Имя базы данных
DB_NAME = getenv("DB_NAME")
# Публичный ключ WireGuard
WG_PUBLIC_KEY = getenv("WG_PUBLIC_KEY")
# Приватный ключ WireGuard
WG_PRIVATE_KEY = getenv("WG_PRIVATE_KEY")
# Входная точка (публичный IP-адрес) сервера
WG_ENDPOINT = getenv("WG_ENDPOINT")
# Api ID Telegram
API_ID = int(getenv('API_ID'))
# Api Hash Telegram
API_HASH = getenv("API_HASH")
# Токен бота Telegram
BOT_TOKEN = getenv("BOT_TOKEN")
# Токен бота для оплаты
PAYMENT_BOT_TOKEN = getenv("PAYMENT_BOT_TOKEN")
# Тестовый токен оплаты Сбербанк
SBERBANK_TEST_TOKEN = getenv("SBERBANK_TEST_TOKEN")
# Номер для принятия платежей Сбербанк
SBERBANK_NUMBER = getenv("SBERBANK_NUMBER")
# ID канала поддержки
SUPPORT_ID = int(getenv("SUPPORT_ID"))
# TG_ID админа
ADMIN_ID = int(getenv("ADMIN_ID"))
