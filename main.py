from UserManager import UserManager, get_user_keypair


if __name__ == "__main__":
    manager = UserManager()
    manager.create_database_connection()
    #manager.delete_user_by_ip(11)
    #manager.create_user("Test123456")
    # for usr in manager._database.get_all_users():
    #     print(usr)

    # ip = manager._database.get_free_ip()
    # print(manager._database.get_keys_by_ip(ip))
    #
    # print(manager.fill_config_free_users())


    # for allowed_IP in range(14, 254):
    #     keypair = get_user_keypair()
    #     manager._database.cursor.execute(f"INSERT INTO wg_user(publickey, privatekey, allowed_ip) VALUES("
    #                         f"'{keypair.public_key}',"
    #                         f"'{keypair.private_key}',"
    #                         f"{allowed_IP})")
    #     print(f'{keypair} added')
    # manager._database.connection.commit()

    # for allowed_IP in range(14, 254):
    #     manager._database.cursor.execute(f"DELETE FROM wg_user WHERE allowed_ip = {allowed_IP}")
    #     print(f"{allowed_IP} deleted")
    #
    # manager._database.connection.commit()
    # configs = manager.get_configs_list_for_user(1214900768)
    # print(configs)
