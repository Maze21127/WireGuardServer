from UserManager import UserManager
import datetime
from bot import logger

manager = UserManager()
manager.create_database_connection()

users = manager._database.get_all_users_subscriptions_info()

for user in users:
    if (user.end_date - datetime.date.today()).days < 1:
        manager.deactivate_user(user.tg_id)
        logger.info(f"Пользователь {user.tg_id} деактивирован")
        print(f"Пользователь {user.tg_id} деактивирован")

