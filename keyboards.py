from telethon import Button
from settings import ADMIN_ID


def get_keyboard(tg_id: int) -> list:
    if tg_id == ADMIN_ID:
        return admin_keyboard
    else:
        return keyboard


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


subscribe_keyboard = [
    [Button.text(price_button, resize=True)],
    [Button.text(start_subscribe, resize=True)],
    [Button.text(main_menu, resize=True)],

]