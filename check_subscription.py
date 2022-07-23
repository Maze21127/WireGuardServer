from UserManager import UserManager
import datetime
from logger import logger

logger.info(f"Start check subscriptions {datetime.datetime.now()}")
print("Start check subscriptions", datetime.datetime.now())
manager = UserManager()
manager.create_database_connection()

users = manager._database.get_all_users_subscriptions_info()

for user in users:
    if (user.end_date - datetime.date.today()).days < 1:
        manager.deactivate_user(user.tg_id)
        logger.info(f"Пользователь {user.tg_id} деактивирован")
        print(f"Пользователь {user.tg_id} деактивирован")

print("End check subscriptions", datetime.datetime.now())
logger.info(f"End check subscriptions {datetime.datetime.now()}")