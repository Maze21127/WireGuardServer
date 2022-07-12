from os import getenv
from dotenv import load_dotenv


load_dotenv('.env')

DB_HOST = getenv('DB_HOST')
DB_USER = getenv("DB_USER")
DB_PASSWORD = getenv("DB_PASSWORD")
DB_NAME = getenv("DB_NAME")
WG_PUBLIC_KEY = getenv("WG_PUBLIC_KEY")
WG_ENDPOINT = getenv("WG_ENDPOINT")
API_ID = int(getenv('API_ID'))
API_HASH = getenv("API_HASH")
BOT_TOKEN = getenv("BOT_TOKEN")
SUPPORT_ID = int(getenv("SUPPORT_ID"))