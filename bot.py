import asyncio
import re
from datetime import datetime

from telethon import TelegramClient, events, Button, types, functions

from Entities import *
from UserManager import UserManager
from exceptions import NoFreeIpAddress
from settings import *


def generate_invoice(price_label: str, price_amount: int, currency: str, title: str,
                     description: str, payload: str, start_param: str) -> types.InputMediaInvoice:
    price = types.LabeledPrice(label=price_label, amount=price_amount)  # label - just a text, amount=10000 means 100.00
    invoice = types.Invoice(
        currency=currency,  # currency like USD
        prices=[price],  # there could be a couple of prices.
        test=True,  # if you're working with test token

        #  next params are saying for themselves
        name_requested=False,
        phone_requested=False,
        email_requested=False,
        shipping_address_requested=False,
        flexible=False,
        phone_to_provider=False,
        email_to_provider=False
    )

    return types.InputMediaInvoice(
        title=title,
        description=description,
        invoice=invoice,
        payload=payload.encode("UTF-8"),  # payload, which will be sent to next 2 handlers
        provider=SBERBANK_TEST_TOKEN,
        provider_data=types.DataJSON("{}"),  # honestly, no idea.
        start_param=start_param,
        # start_param will be passed with UpdateBotPrecheckoutQuery,
        # I don't really know why is it needed, I guess like payload.
    )


bot = TelegramClient("WireGuardVPN_newBot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)
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
start_subscribe = "Оплатить подписку"
price_button = "Информация"

black_list = [instruction, subscribe, configurations, create_configuration, show_configurations, delete_configuration,
              main_menu, support, back, cancel, start_subscribe, price_button, '/support']

keyboard = [
    [
        Button.text(instruction, resize=True),
        Button.text(subscribe, resize=True)
    ],
    [
        Button.text(configurations, resize=True),
    ]
]

configs_keyboard = [
    [Button.text(show_configurations)],
    [Button.text(create_new_configuration)],
    [Button.text(delete_configuration)],
    [Button.text(main_menu)]
]

subscribe_keyboard = [
    [Button.text(price_button, resize=True)],
    [Button.text(start_subscribe, resize=True)],
    [Button.text(main_menu, resize=True)],

]


@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    user = event.sender
    tg_user = TgUser(user.id, user.username, user.first_name, user.last_name, user.phone)
    print(tg_user)
    #manager.add_new_user(tg_user)
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


@bot.on(events.NewMessage(pattern=price_button))
async def callback(event):
    price = manager.get_subscription_info_by_id(event.peer_id.user_id)
    # TODO: Делать запрос в бд на количество подписок, отправлять это количество
    # TODO: Делать запрос в бд на дату окончания подписки, отправлять ее если она не бесконечная
    if price == 2147483647:
        price_message = "У вас неограниченная подписка."
    else:
        price_message = f"Стоимость - {price}р в месяц."
    await event.respond("Ввиду того, что государство начало блокировку различных VPN-сервисов, было "
                        "принято решение, не делать годовую подписку, а ограничиться только ежемесячной\n")
    await event.respond(f"{price_message}\n"
                        "Можно создать до 5 конфигурационных файлов и использовать одновременно на 5 устройствах")
    if price != 2147483647:
        await event.respond(f"Функция оплаты подписки через бота появится позже")
    await event.respond("Выберите действие", buttons=subscribe_keyboard)
    #await event.respond(f"Хотите узнать что-то еще?", buttons=keyboard)


@bot.on(events.Raw(types.UpdateNewMessage))
async def payment_received_handler(event):
    if isinstance(event.message.action, types.MessageActionPaymentSentMe):
        payment: types.MessageActionPaymentSentMe = event.message.action
        print(payment)
        print(event.message.peer_id.user_id)
        print("Оплата прошла")
        if payment.payload.decode("UTF-8") == '1MonthSubscribe':
            await bot.send_message(event.message.peer_id.user_id, "Спасибо за оплату подписки,"
                                                          "теперь вы можете получить конфиг")

        raise events.StopPropagation


@bot.on(events.Raw(types.UpdateBotPrecheckoutQuery))
async def payment_pre_checkout_handler(event: types.UpdateBotPrecheckoutQuery):
    if event.payload.decode("UTF-8") == '1MonthSubscribe':
        #  so we have to confirm payment
        await bot(
            functions.messages.SetBotPrecheckoutResultsRequest(
                query_id=event.query_id,
                success=True,
                error=None
            )
        )

    else:
        # for example, something went wrong (whatever reason). We can tell customer about that:
        await bot(
            functions.messages.SetBotPrecheckoutResultsRequest(
                query_id=event.query_id,
                success=False,
                error="Что-то пошло не так, пожалуйста, напишите в поддержку"
            )
        )

    raise events.StopPropagation


@bot.on(events.NewMessage(pattern=subscribe))
async def callback(event):
    await event.respond("Выберите действие", buttons=subscribe_keyboard)


@bot.on(events.NewMessage(pattern=start_subscribe))
async def callback(event):
    file = generate_invoice("Pay", 15000, "RUB", "Подписка", "Подписка на 1 месяц", "1MonthSubscribe", "abc")
    await bot.send_file(event.chat_id, file)
    #await bot.send_message(event.chat_id, "Сначала нужно оформить подписку", buttons=configs_keyboard)

    #await event.respond("Выберите действие", buttons=configs_keyboard)


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
            print(f"Файл конфигурации отправлен пользователю {event.peer_id.user_id}")
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
        print(f"Файл конфигурации {answer_message} удален пользователем {event.peer_id.user_id}")
        break


@bot.on(events.NewMessage(pattern=main_menu))
async def callback(event):
    await event.respond(f"Хотите узнать что-то еще?", buttons=keyboard)


@bot.on(events.NewMessage(pattern="/support"))
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

