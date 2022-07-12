from telethon import TelegramClient

api_id = 19466009
api_hash = '997bafd0a9343f21a488fa72cb6a5325'


client = TelegramClient("current_session", api_id, api_hash)


async def main():

    user = await client.get_entity(804339009)
    print(user)
    print(user.username)


if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())