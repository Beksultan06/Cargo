from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from django.conf import settings

def get_inline_keyboard(registration=False, chat_id=None):
    buttons = [
        [InlineKeyboardButton(text="💬 Написать менеджеру", url="https://www.youtube.com/")]
    ]
    if registration and chat_id:
        registration_url = f"{settings.SITE_BASE_URL}/?chat_id={chat_id}"
        buttons.append([
            InlineKeyboardButton(
                text='📝 Пройти регистрацию',
                web_app=WebAppInfo(url=registration_url)
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧑‍💼 Профиль"), KeyboardButton(text="📍 Адреса"), KeyboardButton(text="📦 Мои посылки")],
            [KeyboardButton(text="📕 Инструкция"), KeyboardButton(text="🚫 Запрещенные товары"), KeyboardButton(text="⚙️ Поддержка")],
            [KeyboardButton(text="ℹ️ О нас"), KeyboardButton(text="✅ Добавить трек")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_profile_buttons(chat_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔑 Войти в личный кабинет",
                    web_app=WebAppInfo(url=f"{settings.SITE_BASE_URL}/cargopart/?chat_id={chat_id}")
                )
            ]
        ]
    )
    return keyboard

def get_support_buttons():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📲 Написать на WhatsApp", url="https://www.youtube.com/")],
            [InlineKeyboardButton(text="📷 Наш инстаграм", url="https://www.youtube.com/")]
        ]
    )
    return keyboard

def get_whatsapp_manager_button():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📲 WhatsApp менеджера", url="https://www.youtube.com/")]
        ]
    )
    return keyboard



def get_package_options_keyboard(track_number):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🏢 Забрать со склада", callback_data=f"pickup_{track_number}"),
            InlineKeyboardButton(text="🚚 Доставить", callback_data=f"deliver_{track_number}")
        ]
    ])
    return keyboard