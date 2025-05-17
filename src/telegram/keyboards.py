from aiogram.types import (
                        InlineKeyboardMarkup,
                        InlineKeyboardButton,
                        ReplyKeyboardMarkup,
                        KeyboardButton)
from aiogram.types.web_app_info import WebAppInfo
from aiogram.filters.callback_data import CallbackData
from src.database.queries.orm import db


app_link = 'https://ir-wb-auto.ru/?v=2'

back_button = [InlineKeyboardButton(text='<< Меню', callback_data='back')]

to_menu = InlineKeyboardMarkup(inline_keyboard=[back_button])

class MyCallback(CallbackData, prefix="my"):
    string: str
    value: bool

def create_payment_kb(payment_url: str):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Оплатить', url=payment_url)], 
            back_button
        ]
    )

async def settings_kb(chat_id) -> InlineKeyboardMarkup:
    status = await db.get_notifications_status(chat_id)
    if status:
        btn_text = "🔕 Выключить уведомления"
    else:
        btn_text = "🔔 Включить уведомления"
        
    return InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text='🔑 Токен WB', callback_data='wb_token'), 
                                InlineKeyboardButton(text='📝 Обновить артикулы', web_app=WebAppInfo(url=app_link))],
                                [InlineKeyboardButton(text=btn_text, 
                                                      callback_data=MyCallback(
                                                                                string="notification",
                                                                                value=status).pack())],
                                back_button
                                ])



pinned_menu = ReplyKeyboardMarkup(
                                keyboard=[
                                    [KeyboardButton(text='🏠 Меню')]
                                    ], 
                                resize_keyboard=True,
                                is_persistent=True)

async def start_menu(chat_id):
    menu_list = [
        [InlineKeyboardButton(text='📘 Как пользоваться?', callback_data='guide')],
        [InlineKeyboardButton(text='⚙️ Настройки', callback_data='user_settings'), 
        InlineKeyboardButton(text='🛒 Подписка', callback_data='subscribe_status')],
        ]
    trial_status = await db.check_trial(chat_id)
    if trial_status:
        menu_list.append(
            [InlineKeyboardButton(text='🎁 Пробный период', callback_data='trial')]
        )
    return InlineKeyboardMarkup(inline_keyboard=menu_list)

trial_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Активировать пробный период', callback_data='activate_trial')],
    back_button
])

help_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🎥 Видео', url='example.com'), 
    InlineKeyboardButton(text='Текстовый гайд', callback_data='text_guide')],
    back_button])

sub_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Оформить подписку (1 месяц)', callback_data='buy_sub')],
    back_button
])



