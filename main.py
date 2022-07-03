from UserManager import UserManager


if __name__ == "__main__":
    manager = UserManager()
    manager.create_database_connection()
    #manager.delete_user_by_ip(11)
    #manager.create_user("Test123456")
    for usr in manager._database.get_all_users():
        print(usr)
