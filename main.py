from telethon import TelegramClient
from settings import SESSION, API_ID, API_HASH, BOT_TOKEN

from UserManager import UserManager
from bot import *

bot = TelegramClient(SESSION, API_ID, API_HASH).start(bot_token=BOT_TOKEN)
manager = UserManager()
manager.create_database_connection()


if __name__ == "__main__":
    print("Бот запущен")
    bot.run_until_disconnected()