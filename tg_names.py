from telethon import TelegramClient

api_id = 19466009
api_hash = '997bafd0a9343f21a488fa72cb6a5325'


client = TelegramClient("lera", api_id, api_hash)


async def main():

    user = await client.get_entity(455035418)
    print(user)
    print(f'{user.id=}')
    print(f'{user.username=}')
    print(f'{user.first_name=}')
    print(f'{user.last_name=}')
    print(f'{user.phone=}')


if __name__ == '__main__':
    with client:
        client.loop.run_until_complete(main())