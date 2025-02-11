from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from django.conf import settings
from asgiref.sync import sync_to_async
from app.web_app.models import User

async def get_inline_keyboard(chat_id=None):
    buttons = [
        [InlineKeyboardButton(text="💬 Написать менеджеру", url="https://www.youtube.com/")]
    ]

    if chat_id:
        user_exists = await sync_to_async(User.objects.filter(chat_id=chat_id).exists)()
        if user_exists:
            # Пользователь найден, генерируем ссылку для автоавторизации
            login_url = f"{settings.SITE_BASE_URL}/cargopart/?chat_id={chat_id}&auto_login=true"
            buttons.append([
                InlineKeyboardButton(
                    text='🔑 Войти в личный кабинет',
                    web_app=WebAppInfo(url=login_url)
                )
            ])
        else:
            # Пользователь не найден, предлагаем регистрацию
            registration_url = f"{settings.SITE_BASE_URL}/register/?chat_id={chat_id}"
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

async def get_profile_buttons(chat_id):
    user_exists = await sync_to_async(User.objects.filter(chat_id=chat_id).exists)()
    
    if user_exists:
        login_url = f"{settings.SITE_BASE_URL}/cargopart/?chat_id={chat_id}&auto_login=true"
        button_text = "🔑 Войти в личный кабинет"
    else:
        login_url = f"{settings.SITE_BASE_URL}/?chat_id={chat_id}"
        button_text = "📝 Пройти регистрацию"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=button_text,
                    web_app=WebAppInfo(url=login_url)
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

def get_profile_courier():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Адреса")],
            [KeyboardButton(text="📕 Инструкция"), KeyboardButton(text="⚙️ Поддержка")],
            [KeyboardButton(text="ℹ️ О нас")]
        ],
        resize_keyboard=True
    )
    return keyboard