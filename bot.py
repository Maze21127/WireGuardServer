import asyncio
import os
from datetime import datetime

from telethon import TelegramClient, events, Button

from settings import *

bot = TelegramClient("WireGuardVPN", API_ID, API_HASH).start(bot_token=BOT_TOKEN)


instruction = "Инструкция"
payment = "Стоимость"
configurations = "Конфигурации"
create_configuration = "Создать конфигурационный файл"
show_configurations = "Показать мои конфигурации"
create_new_configuration = "Создать новую конфигурацию"
configs = os.listdir("configs")  # TODO: Конфигурации будут браться из базы данных для каждого пользователя
main_menu = "Основное меню"
support = "Написать в поддержку"

keyboard = [
    [
        Button.text(instruction, resize=True),
        Button.text(payment, resize=True)
    ],
    [
        Button.text(configurations, resize=True),
        Button.text(support, resize=True)
    ]
]

configs_keyboard = [
    [Button.text(show_configurations)],
    [Button.text(create_new_configuration)],
    [Button.text(main_menu)]
]


@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond(f"Привет {event.sender.first_name}, давай я расскажу тебе, как использовать VPN",
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


@bot.on(events.NewMessage(pattern=payment))
async def callback(event):
    price = 150  # TODO: Стоимость будет браться из базы данных
    await event.respond("Ввиду того, что государство начало блокировку различных VPN-сервисов, было "
                        "принято решение, не делать годовую подписку, а ограничиться только ежемесячной\n")
    await event.respond(f"Стоимость - {price}р в месяц.\n"
                        "Можно создать до 5 конфигурационных файлов и использовать одновременно на 5 устройствах")
    await event.respond(f"Хотите узнать что-то еще?", buttons=keyboard)


@bot.on(events.NewMessage(pattern=configurations))
async def callback(event):
    await event.respond("Выберите действие", buttons=configs_keyboard)


@bot.on(events.NewMessage(pattern=show_configurations))
async def callback(event):
    configs_buttons = [[Button.text(name.split(".conf")[0], resize=True)] for name in configs]
    configs_buttons.append([Button.text("Назад", resize=True)])
    await bot.send_message(event.chat_id, "Выберите конфигурацию", buttons=configs_buttons)
    #await bot.delete_messages(event.chat_id, event.message_id)

    while True:
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("Нажмите на название, чтобы получить конфигурационный файл")
            try:
                answer = await conv.get_response()
                answer_message = answer.message
            except asyncio.TimeoutError:
                answer_message = "Назад"
        if answer_message == "Назад":
            await event.respond("Выберите действие", buttons=configs_keyboard)
            break
        if f"{answer_message}.conf" in configs:
            await bot.send_file(event.chat_id, f"configs/{answer_message}.conf")
            # TODO: Сделать отправку QR-Кода
            #await bot.send_message(event.chat_id, "Выберите конфигурацию", buttons=configs_keyboard)
        else:
            return


@bot.on(events.NewMessage(pattern=create_new_configuration))
async def callback(event):
    if len(configs) == 1:
        await bot.send_message(event.chat_id, "У вас уже максимальное количество конфигураций")
        await bot.send_message(event.chat_id, "Выберите действие", buttons=configs_keyboard)
        return
    while True:
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("Введите название (до 12 символов, без пробелов")
            answer = await conv.get_response()
            if len(answer.message) > 12:
                await conv.send_message("Название слишком длинное")
            else:
                filename = answer.message
                await conv.send_message("Файл конфигурации успешно создан")
                # TODO: Создать и отправить файл, с QR-Кодом
                break
    await event.respond("Выберите действие", buttons=configs_keyboard)


@bot.on(events.NewMessage(pattern=main_menu))
async def callback(event):
    await event.respond(f"Хотите узнать что-то еще?", buttons=keyboard)


@bot.on(events.NewMessage(pattern=support))
async def callback(event):
    # TODO: Добавить оповещение об отправленном сообщении
    async with bot.conversation(event.chat_id) as conv:
        await conv.send_message("Введите сообщение, которое будет отправленно администратору",
                                buttons=Button.text("Отмена", resize=True))
        while True:
            try:
                answer = await conv.get_response()
                if answer.message in (instruction, payment, configurations, support, "Отмена"):
                    await event.respond(f"Хотите узнать что-то еще?", buttons=keyboard)
                    break
                answer.date = datetime.now()
                message = f"Сообщение от {answer.chat_id}\n{answer.date.strftime('%d.%m.%y %H:%M:%S')}\n{answer.message}"
                await bot.send_message(SUPPORT_ID, message)
                break
            except asyncio.TimeoutError:
                continue




if __name__ == "__main__":
    print("Бот запущен")
    bot.run_until_disconnected()

