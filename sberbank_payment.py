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