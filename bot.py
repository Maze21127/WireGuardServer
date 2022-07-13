import asyncio
import re
from datetime import datetime

from telethon import TelegramClient, events, Button

from UserManager import UserManager
from exceptions import NoFreeIpAddress
from settings import *

bot = TelegramClient("WireGuardVPN", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
manager = UserManager()
manager.create_database_connection()


instruction = "Инструкция"
subscribe = "Подписка"
configurations = "Конфигурации"
create_configuration = "Создать конфигурационный файл"
show_configurations = "Показать мои конфигурации"
create_new_configuration = "Создать новую конфигурацию"
delete_configuration = "Удалить конфигурацию"
main_menu = "Основное меню"
support = "Написать в поддержку"
back = "Назад"
cancel = "Отмена"

black_list = [instruction, subscribe, configurations, create_configuration, show_configurations, delete_configuration,
              main_menu, support, back, cancel]

keyboard = [
    [
        Button.text(instruction, resize=True),
        Button.text(subscribe, resize=True)
    ],
    [
        Button.text(configurations, resize=True),
        Button.text(support, resize=True)
    ]
]

configs_keyboard = [
    [Button.text(show_configurations)],
    [Button.text(create_new_configuration)],
    [Button.text(delete_configuration)],
    [Button.text(main_menu)]
]


@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    print(event.sender)
    if event.sender.first_name is not None:
        user = event.sender.first_name
    elif event.sender.username is not None:
        user = event.sender.username
    else:
        user = "Дружище"
    await event.respond(f"Привет {user}, давай я расскажу тебе, как использовать VPN\n\n"
                        f"[INFO] БОТ НАХОДИТСЯ В СТАДИИ ТЕСТИРОВАНИЯ.\n"
                        f"Просьба писать в поддержку в случае любой ошибки",
                        buttons=keyboard)


@bot.on(events.NewMessage(pattern=instruction))
async def callback(event):
    await bot.send_message(event.chat_id, "1. Скачать приложение\n"
                                          "📱 [App Store](https://apps.apple.com/ru/app/wireguard/id1441195209)\n"
                                          "📞 [Google Play](https://play.google.com/store/apps/details?id=com.wireguard"
                                          ".android)\n"
                                          "2. Скачать ваш конфигурационный файл\n"
                                          "3. Добавить его в приложение", link_preview=False, buttons=Button.clear())
    await bot.send_file(event.chat_id, [
        "Screenshots/import_tunnel.jpg",
        "Screenshots/from_file.jpg",
        "Screenshots/allow_vpn.jpg"
    ])
    await event.respond(f"Для Android инструкция аналогична")
    await event.respond(f"Хотите узнать что-то еще?", buttons=keyboard)


@bot.on(events.NewMessage(pattern=subscribe))
async def callback(event):
    price = manager.get_price_by_id(event.peer_id.user_id)
    if price == 2147483647:
        price_message = "У вас неограниченная подписка."
    else:
        price_message = f"Стоимость - {price}р в месяц."
    await event.respond("Ввиду того, что государство начало блокировку различных VPN-сервисов, было "
                        "принято решение, не делать годовую подписку, а ограничиться только ежемесячной\n")
    await event.respond(f"{price_message}\n"
                        "Можно создать до 5 конфигурационных файлов и использовать одновременно на 5 устройствах")
    await event.respond(f"Хотите узнать что-то еще?", buttons=keyboard)


@bot.on(events.NewMessage(pattern=configurations))
async def callback(event):
    if not manager.is_user_active(event.peer_id.user_id):
        await bot.send_message(event.chat_id, "Сначала нужно оформить подписку", buttons=configs_keyboard)
        return
    await event.respond("Выберите действие", buttons=configs_keyboard)


@bot.on(events.NewMessage(pattern=show_configurations))
async def callback(event):
    configs = manager.get_configs_list_for_user(event.peer_id.user_id)

    if len(configs) == 0:
        await bot.send_message(event.chat_id, "У вас нет ни одной конфигурации", buttons=configs_keyboard)
        return

    configs_buttons = [[Button.text(name.split(".conf")[0], resize=True)] for name in configs]
    configs_buttons.append([Button.text("Назад", resize=True)])
    await bot.send_message(event.chat_id, "Выберите конфигурацию", buttons=configs_buttons)

    while True:
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("Нажмите на название, чтобы получить конфигурационный файл")
            try:
                answer = await conv.get_response()
                answer_message = answer.message
            except asyncio.TimeoutError:
                answer_message = "Назад"
        if answer_message in black_list:
            await event.respond(f"Выберите действие", buttons=configs_keyboard)
            break
        config, qr_code = manager.create_user_config_by_name(answer_message, event.peer_id.user_id)
        await bot.send_file(event.chat_id, qr_code)
        await bot.send_file(event.chat_id, config)
        break
    await event.respond("Выберите действие", buttons=configs_keyboard)
        #await bot.send_message(event.chat_id, "Выберите конфигурацию", buttons=configs_keyboard)


@bot.on(events.NewMessage(pattern=create_new_configuration))
async def callback(event):
    configs = manager.get_configs_list_for_user(event.peer_id.user_id)

    if len(configs) == 5:
        await bot.send_message(event.chat_id, "У вас уже максимальное количество конфигураций", buttons=configs_keyboard)
        return

    while True:
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("Введите название (Только английские буквы и цифры)")
            try:
                answer = await conv.get_response()
                config_name = answer.message
            except asyncio.TimeoutError:
                await event.respond("Выберите действие", buttons=configs_keyboard)
                break

            if config_name in black_list:
                await event.respond(f"Выберите действие", buttons=configs_keyboard)
                break

            if len(config_name) >= 254:
                await conv.send_message("Название слишком длинное")
                break

            if not re.match(r"^[a-zA-Z0-9]+$", config_name):
                await conv.send_message("Название содержит пробелы, русские символы или спецсимволы")
                break

            try:
                manager.create_new_config(config_name, event.peer_id.user_id)
            except NoFreeIpAddress:
                await conv.send_message("Нельзя создать конфигурацию, письмо в поддержку уже отправлено")
                await bot.send_message(SUPPORT_ID, f"Пользователь {event.peer_id.user_id} не смог получить конфиг,"
                                                   f"закончились IP-адреса")
                break

            config, qr_code = manager.create_user_config_by_name(config_name, event.peer_id.user_id)
            await conv.send_message("Файл конфигурации успешно создан")
            await bot.send_file(event.chat_id, qr_code)
            await bot.send_file(event.chat_id, config)
            manager.delete_user_config(config_name)
            break
    await event.respond("Выберите действие", buttons=configs_keyboard)


@bot.on(events.NewMessage(pattern=delete_configuration))
async def callback(event):
    configs = manager.get_configs_list_for_user(event.peer_id.user_id)
    configs_buttons = [[Button.text(name.split(".conf")[0], resize=True)] for name in configs]
    configs_buttons.append([Button.text("Назад", resize=True)])
    await bot.send_message(event.chat_id, "Выберите конфигурацию для удаления", buttons=configs_buttons)

    while True:
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("Нажмите на название, чтобы удалить конфигурационный файл")
            try:
                answer = await conv.get_response()
                answer_message = answer.message
                if answer_message in black_list:
                    await event.respond(f"Хотите узнать что-то еще?", buttons=configs_keyboard)
                    break
            except asyncio.TimeoutError:
                await event.respond("Выберите действие", buttons=configs_keyboard)
                break

        manager.delete_user_config_by_name(answer_message, event.peer_id.user_id)
        await event.respond(f"Конфигурация {answer_message} удалена", buttons=configs_keyboard)
        break


@bot.on(events.NewMessage(pattern=main_menu))
async def callback(event):
    await event.respond(f"Хотите узнать что-то еще?", buttons=keyboard)


@bot.on(events.NewMessage(pattern=support))
async def callback(event):
    async with bot.conversation(event.chat_id) as conv:
        await conv.send_message("Введите сообщение, которое будет отправленно администратору",
                                buttons=Button.text("Отмена", resize=True))
        while True:
            try:
                answer = await conv.get_response()
                if answer.message in black_list:
                    await event.respond(f"Хотите узнать что-то еще?", buttons=keyboard)
                    break
                answer.date = datetime.now()
                message = f"ID: {answer.peer_id.user_id}\n{answer.date.strftime('%d.%m.%y %H:%M:%S')}\n" \
                          f"{answer.message}"
                await bot.send_message(SUPPORT_ID, message)
                await event.respond("Сообщение в поддержку отправлено", buttons=keyboard)
                break
            except asyncio.TimeoutError:
                continue


if __name__ == "__main__":
    print("Бот запущен")
    bot.run_until_disconnected()

