import asyncio
import random
import re

from telethon import TelegramClient, events, Button

from Entities import *
from UserManager import UserManager
from exceptions import NoFreeIpAddress
from logger import logger
from settings import *


def get_payment_string() -> str:
    chars = '+-/*!&$#?=@<>abcdefghijklnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    LENGTH = 16
    return "".join([random.choice(chars) for _ in range(LENGTH)])


# Функция для генерации сообщения с оплатой
# def generate_invoice(price_label: str, price_amount: int, currency: str, title: str,
#                      description: str, payload: str, start_param: str) -> types.InputMediaInvoice:
#     price = types.LabeledPrice(label=price_label, amount=price_amount)  # label - just a text, amount=10000 means 100.00
#     invoice = types.Invoice(
#         currency=currency,  # currency like USD
#         prices=[price],  # there could be a couple of prices.
#         test=True,  # if you're working with test token
#
#         #  next params are saying for themselves
#         name_requested=False,
#         phone_requested=False,
#         email_requested=False,
#         shipping_address_requested=False,
#         flexible=False,
#         phone_to_provider=False,
#         email_to_provider=False
#     )
#
#     return types.InputMediaInvoice(
#         title=title,
#         description=description,
#         invoice=invoice,
#         payload=payload.encode("UTF-8"),  # payload, which will be sent to next 2 handlers
#         provider=SBERBANK_TEST_TOKEN,
#         provider_data=types.DataJSON("{}"),  # honestly, no idea.
#         start_param=start_param,
#         # start_param will be passed with UpdateBotPrecheckoutQuery,
#         # I don't really know why is it needed, I guess like payload.
#     )

bot = TelegramClient(SESSION, API_ID, API_HASH).start(bot_token=BOT_TOKEN)
manager = UserManager()
manager.create_database_connection()

instruction = "Инструкция"
subscribe = "Подписка"
configurations = "Конфигурации"
create_configuration = "Создать конфигурационный файл"
show_configurations = "Показать мои конфигурации"
create_new_configuration = "Создать новую конфигурацию"
rename_configuration = "Переименовать конфигурацию"
main_menu = "Основное меню"
support = "Написать в поддержку"
back = "Назад"
cancel = "Отмена"
start_subscribe = "Оплатить подписку"
price_button = "Информация"
admin = "Админ"
payment_requests = "Заявки на оплату"

black_list = [instruction, subscribe, configurations, create_configuration, show_configurations, rename_configuration,
              main_menu, support, back, cancel, start_subscribe, price_button, '/support', admin, payment_requests]

keyboard = [
    [
        Button.text(instruction, resize=True),
        Button.text(subscribe, resize=True)
    ],
    [
        Button.text(configurations, resize=True),
    ]
]

admin_keyboard = [
    [
        Button.text(instruction, resize=True),
        Button.text(subscribe, resize=True)
    ],
    [
        Button.text(configurations, resize=True),
    ],
    [
        Button.text(admin, resize=True),
    ]
]

admin_panel = [
    [
        Button.text(payment_requests, resize=True),
        Button.text(main_menu, resize=True)
    ]
]

configs_keyboard = [
    [Button.text(show_configurations)],
    [Button.text(create_new_configuration)],
    [Button.text(rename_configuration)],
    [Button.text(main_menu)]
]

# configs_keyboard = [
#     [Button.text(show_configurations)],
#     [Button.text(create_new_configuration)],
#     [Button.text(main_menu)]
# ]


subscribe_keyboard = [
    [Button.text(price_button, resize=True)],
    [Button.text(start_subscribe, resize=True)],
    [Button.text(main_menu, resize=True)],

]


def get_keyboard(tg_id: int) -> list:
    if tg_id == ADMIN_ID:
        return admin_keyboard
    else:
        return keyboard


@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    user = event.sender
    tg_user: TgUser = TgUser(user.id, user.username, user.first_name, user.last_name, user.phone)
    manager.add_new_user(tg_user)
    if event.sender.first_name is not None:
        user = event.sender.first_name
    elif event.sender.username is not None:
        user = event.sender.username
    else:
        user = "Дружище"
    await event.respond(f"Привет, {user}, давай я расскажу тебе, как использовать VPN\n\n"
                        f"[INFO] БОТ НАХОДИТСЯ В СТАДИИ ТЕСТИРОВАНИЯ.\n"
                        f"Просьба писать в поддержку в случае любой ошибки",
                        buttons=get_keyboard(tg_user.tg_id))
    logger.info(f"{event.sender.id} нажал /start")


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
    await event.respond(f"Хотите узнать что-то еще?", buttons=get_keyboard(event.sender.id))

    logger.info(f"{event.sender.id} нажал Инструкция")


@bot.on(events.NewMessage(pattern=price_button))
async def callback(event):
    user_subscription: UserSubscription = manager.get_subscription_info_by_id(event.peer_id.user_id)
    if user_subscription.price == 2147483647:
        price_message = "У вас неограниченная подписка.\n"
    else:
        price_message = f"**Стоимость - {user_subscription.price}р в месяц.**\n"

        if user_subscription.end_date is not None:
            price_message += f"**Ваша подписка действует до {user_subscription.end_date.strftime('%d.%m.%y')}\n"

    await event.respond(f"{price_message}"
                        f"Максимальное количество устройств - {user_subscription.max_configs}.\n"
                        f"На каждом устройстве необходимо использовать свой конфигурационный файл.")

    await event.respond("Выберите действие", buttons=subscribe_keyboard)
    logger.info(f"{event.sender.id} нажал Информация")


# @bot.on(events.Raw(types.UpdateNewMessage))
# async def payment_received_handler(event):
#     if isinstance(event.message.action, types.MessageActionPaymentSentMe):
#         payment: types.MessageActionPaymentSentMe = event.message.action
#         print(payment)
#         print(event.message.peer_id.user_id)
#         print("Оплата прошла")
#         if payment.payload.decode("UTF-8") == '1MonthSubscribe':
#             await bot.send_message(event.message.peer_id.user_id, "Спасибо за оплату подписки,"
#                                                                   "теперь вы можете получить конфиг")
#
#         raise events.StopPropagation


#
# @bot.on(events.Raw(types.UpdateBotPrecheckoutQuery))
# async def payment_pre_checkout_handler(event: types.UpdateBotPrecheckoutQuery):
#     if event.payload.decode("UTF-8") == '1MonthSubscribe':
#         #  so we have to confirm payment
#         await bot(
#             functions.messages.SetBotPrecheckoutResultsRequest(
#                 query_id=event.query_id,
#                 success=True,
#                 error=None
#             )
#         )
#
#     else:
#         # for example, something went wrong (whatever reason). We can tell customer about that:
#         await bot(
#             functions.messages.SetBotPrecheckoutResultsRequest(
#                 query_id=event.query_id,
#                 success=False,
#                 error="Что-то пошло не так, пожалуйста, напишите в поддержку"
#             )
#         )
#
#     raise events.StopPropagation


@bot.on(events.NewMessage(pattern=subscribe))
async def callback(event):
    await event.respond("Выберите действие", buttons=subscribe_keyboard)
    logger.info(f"{event.sender.id} нажал Подписка")


@bot.on(events.NewMessage(pattern=start_subscribe))
async def callback(event):
    user_subscription: UserSubscription = manager.get_subscription_info_by_id(event.peer_id.user_id)

    if user_subscription.price == 2147483647:
        await event.respond("У вас неограниченная подписка, ничего оплачивать не нужно", buttons=subscribe_keyboard)
        return

    if manager.is_user_have_payment_request(event.peer_id.user_id):
        logger.info(f"{event.sender.id} попытался создать еще одну заявку")
        return await event.respond("У вас уже есть неоплаченная заявка", buttons=subscribe_keyboard)

    random_string = get_payment_string()
    payment_string = f"{event.peer_id.user_id}/{random_string}"
    date = datetime.datetime.now()

    message = f"ID: {event.message.peer_id.user_id}\n{date.strftime('%d.%m.%y %H:%M:%S')}\n" \
              f"ОПЛАТА: {payment_string}"

    await bot.send_message(SUPPORT_ID, message)
    await event.respond(f"Переведите {user_subscription.price} RUB по номеру {SBERBANK_NUMBER}, "
                        f"указав в описании следующую строку", buttons=subscribe_keyboard)
    await event.respond(
        f"{payment_string}", buttons=subscribe_keyboard)
    await event.respond(f"Если доступ не появится в течении 5 минут после оплаты - пожалуйста, напишите в поддержку")

    manager.create_payment_request(event.message.peer_id.user_id, random_string)
    logger.info(f"{event.sender.id} создал заявку на оплату")

    # await bot.send_message(event.chat_id, "Сначала нужно оформить подписку", buttons=configs_keyboard)

    # await event.respond("Выберите действие", buttons=configs_keyboard)


# @bot.on(events.NewMessage(pattern=start_subscribe))
# async def callback(event):
#     user_subscription: UserSubscription = manager.get_subscription_info_by_id(event.peer_id.user_id)
#     if user_subscription.price == 2147483647:
#         await event.respond("У вас неограниченная подписка, ничего оплачивать не нужно", buttons=subscribe_keyboard)
#         return
#     file = generate_invoice("Pay", user_subscription.price, "RUB", "Подписка", "Подписка на 1 месяц",
#                             "1MonthSubscribe", "abc")
#     await bot.send_file(event.chat_id, file)
#     # await bot.send_message(event.chat_id, "Сначала нужно оформить подписку", buttons=configs_keyboard)
#
#     # await event.respond("Выберите действие", buttons=configs_keyboard)


@bot.on(events.NewMessage(pattern=configurations))
async def callback(event):
    if not manager.is_user_active(event.peer_id.user_id):
        logger.info(f"{event.sender.id} получил сообщение о том, что сначала нужно оформить подписку")
        return await bot.send_message(event.chat_id, "Сначала нужно оформить подписку",
                                      buttons=get_keyboard(event.peer_id.user_id))
    await event.respond("Выберите действие", buttons=configs_keyboard)


@bot.on(events.NewMessage(pattern=show_configurations))
async def callback(event):
    configs = manager.get_configs_list_for_user(event.peer_id.user_id)

    if len(configs) == 0:
        logger.debug(f"{event.sender.id} получил сообщение о том, у него нет конфигураций")
        return await bot.send_message(event.chat_id, "У вас нет ни одной конфигурации", buttons=configs_keyboard)

    configs_buttons = [[Button.text(name.split(".conf")[0], resize=True)] for name in configs]
    configs_buttons.append([Button.text("Назад", resize=True)])
    await bot.send_message(event.chat_id, "Выберите конфигурацию", buttons=configs_buttons)

    while True:
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("Нажмите на название, чтобы получить конфигурационный файл")
            logger.info(f"{event.sender.id} смотрит конфигурации")

            try:
                answer = await conv.get_response()
                answer_message = answer.message
            except asyncio.TimeoutError:
                logger.debug(f"{event.sender.id} TimeoutError")
                return await event.respond(f"Выберите действие", buttons=configs_buttons)

        if answer_message in black_list:
            await event.respond(f"Выберите действие", buttons=configs_keyboard)
            break
        config, qr_code = manager.create_user_config_by_name(answer_message, event.peer_id.user_id)
        await bot.send_file(event.chat_id, qr_code)
        await bot.send_file(event.chat_id, config)
        logger.info(f"{event.sender.id} получил конфигурационный файл")
        break
    await event.respond("Выберите действие", buttons=configs_keyboard)


@bot.on(events.NewMessage(pattern=create_new_configuration))
async def callback(event):
    # TODO: Объединить два запроса в один
    configs = manager.get_configs_list_for_user(event.peer_id.user_id)
    limit = manager.get_subscription_info_by_id(event.peer_id.user_id)

    if len(configs) == limit.max_configs:
        logger.debug(f"{event.sender.id} имеет максимальное число конфигураций")
        return await bot.send_message(event.chat_id, "У вас уже максимальное количество конфигураций",
                                      buttons=configs_keyboard)

    while True:
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("Введите название (Только английские буквы и цифры)")

            try:
                answer = await conv.get_response()
                config_name = answer.message
            except asyncio.TimeoutError:
                logger.debug(f"{event.sender.id} TimeoutError")
                return await event.respond("Выберите действие", buttons=configs_keyboard)

            if config_name in black_list:
                return await event.respond(f"Выберите действие", buttons=configs_keyboard)

            if len(config_name) >= 254:
                logger.debug(f"{event.sender.id} ввел слишком длинное название конфигурации")
                return await event.respond("Название слишком длинное", buttons=configs_keyboard)

            if not re.match(r"^[a-zA-Z0-9]+$", config_name):
                logger.debug(f"{event.sender.id} ввел неверное название конфигурации")
                return await conv.send_message("Название содержит пробелы, русские символы или спецсимволы",
                                               buttons=configs_keyboard)
            break

    try:
        manager.create_new_config(config_name, event.peer_id.user_id)
        logger.info(f"{event.sender.id} создал новый конфиг")
    except NoFreeIpAddress:
        logger.warning(f"{event.sender.id} NoFreeIpAddress")
        await bot.send_message(SUPPORT_ID, f"Пользователь {event.peer_id.user_id} не смог получить конфиг,"
                                           f"закончились IP-адреса")
        return await event.respond("Нельзя создать конфигурацию, письмо в поддержку уже отправлено")

    # TODO: Вынести это в отдельную функцию
    config, qr_code = manager.create_user_config_by_name(config_name, event.peer_id.user_id)
    await bot.send_message(event.chat_id, "Файл конфигурации успешно создан")
    await bot.send_file(event.chat_id, qr_code)
    await bot.send_file(event.chat_id, config)
    logger.info(f"{event.sender.id} создал и получил новый конфиг файл")
    manager.delete_user_config(config_name)
    logger.info(f"{config_name}.conf удален")

    await event.respond("Выберите действие", buttons=configs_keyboard)


@bot.on(events.NewMessage(pattern=rename_configuration))
async def callback(event):
    configs = manager.get_configs_list_for_user(event.peer_id.user_id)
    configs_buttons = [[Button.text(name.split(".conf")[0], resize=True)] for name in configs]
    configs_buttons.append([Button.text("Назад", resize=True)])
    await bot.send_message(event.chat_id, "Выберите конфигурацию для переименования", buttons=configs_buttons)
    logger.info(f'{event.sender.id} решил переименовать конфиг файл')

    while True:
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("Нажмите на название, чтобы переименовать конфигурационный файл")
            try:
                answer = await conv.get_response()
                old_name = answer.message
                if old_name in black_list:
                    await event.respond(f"Хотите узнать что-то еще?", buttons=configs_keyboard)
                    break
            except asyncio.TimeoutError:
                await event.respond("Выберите действие", buttons=configs_keyboard)
                break
        break

    # TODO: Вынести в отдельную функцию
    while True:
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("Введите название (Только английские буквы и цифры)")
            try:
                answer = await conv.get_response()
                config_name = answer.message

            except asyncio.TimeoutError:
                logger.debug(f"{event.sender.id} TimeoutError")
                return await event.respond("Выберите действие", buttons=configs_keyboard)
            if config_name in black_list:
                return await event.respond(f"Выберите действие", buttons=configs_keyboard)
            if len(config_name) >= 254:
                logger.debug(f"{event.sender.id} ввел слишком длинное название конфигурации")
                return await event.respond("Название слишком длинное", buttons=configs_keyboard)
            if not re.match(r"^[a-zA-Z0-9]+$", config_name):
                logger.debug(f"{event.sender.id} ввел неверное название конфигурации")
                return await conv.send_message("Название содержит пробелы, русские символы или спецсимволы",
                                               buttons=configs_keyboard)
        break

    manager.rename_configuration_by_name(old_name, config_name, event.peer_id.user_id)
    await event.respond(f"Конфигурация {old_name} теперь называется {config_name}", buttons=configs_keyboard)
    logger.info(f"{event.sender.id} изменил название у конфиг файла {old_name}")


@bot.on(events.NewMessage(pattern=main_menu))
async def callback(event):
    await event.respond(f"Хотите узнать что-то еще?", buttons=get_keyboard(event.sender.id))
    logger.info(f"{event.sender.id} попал в главное меню")


@bot.on(events.NewMessage(pattern=admin))
async def callback(event):
    if event.sender.id != ADMIN_ID:
        return await event.respond(f"У вас нет доступа", buttons=get_keyboard(event.sender.id))
    await event.respond(f"Выберите действие", buttons=admin_panel)


@bot.on(events.NewMessage(pattern=payment_requests))
async def callback(event):
    if event.sender.id != ADMIN_ID:
        return await event.respond(f"У вас нет доступа", buttons=get_keyboard(event.sender.id))

    # Берем список заявок
    payments = manager.get_payment_requests()

    payments_keyboard = [[Button.text(f"{payment[0]}/{payment[2]}\n{payment[1].strftime('%d.%m.%y %H:%M:%S')}",
                                      resize=True)] for payment in payments]
    payments_keyboard.append([Button.text("Основное меню", resize=True)])

    while True:
        async with bot.conversation(event.chat_id) as conv:
            await conv.send_message("Выберите заявку для подтверждения", buttons=payments_keyboard)

            try:
                answer = await conv.get_response()
                answer_message = answer.message
                break
            except asyncio.TimeoutError:
                return await event.respond("Выберите действие", buttons=payments_keyboard)

    if answer_message in black_list:
        return await event.respond(f"Выберите действие", buttons=admin_panel)

    tg_id = answer_message.split("/")[0]
    manager.accept_payment_request(tg_id)
    await event.respond("Заявка одобрена", buttons=admin_panel)


@bot.on(events.NewMessage(pattern="/support"))
async def callback(event):
    async with bot.conversation(event.chat_id) as conv:
        await conv.send_message("Введите сообщение, которое будет отправленно администратору",
                                buttons=Button.text("Отмена", resize=True))
        while True:
            try:
                answer = await conv.get_response()
                if answer.message in black_list:
                    await event.respond(f"Хотите узнать что-то еще?", buttons=get_keyboard(event.sender.id))
                    break
                answer.date = datetime.datetime.now()
                message = f"ID: {answer.peer_id.user_id}\n{answer.date.strftime('%d.%m.%y %H:%M:%S')}\n" \
                          f"{answer.message}"
                await bot.send_message(SUPPORT_ID, message)
                await event.respond("Сообщение в поддержку отправлено", buttons=get_keyboard(event.sender.id))
                logger.debug(f"{event.sender.id} отправил сообщение в поддержку")
                break
            except asyncio.TimeoutError:
                continue


if __name__ == "__main__":
    print("Бот запущен")
    bot.run_until_disconnected()
