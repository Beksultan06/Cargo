from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from django.conf import settings
from asgiref.sync import sync_to_async
from app.web_app.models import User, Settings

@sync_to_async
def get_settings():
    return Settings.objects.first()

async def get_inline_keyboard(chat_id=None):
    app_settings = await get_settings()
    buttons = [
        [InlineKeyboardButton(text="💬 Написать менеджеру", url=app_settings.watapp or "https://default-link.com/")]
    ]

    if chat_id:
        user_exists = await sync_to_async(User.objects.filter(chat_id=chat_id).exists)()
        if user_exists:
            login_url = f"{settings.SITE_BASE_URL}/cargopart/?chat_id={chat_id}&auto_login=true"
            buttons.append([
                InlineKeyboardButton(
                    text='🔑 Войти в личный кабинет',
                    web_app=WebAppInfo(url=login_url)
                )
            ])
        else:
            registration_url = f"{settings.SITE_BASE_URL}/register/?chat_id={chat_id}"
            buttons.append([
                InlineKeyboardButton(
                    text='📝 Пройти регистрацию',
                    web_app=WebAppInfo(url=registration_url)
                )
            ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

# Основное меню
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

# Кнопки профиля
async def get_profile_buttons(chat_id):
    user_exists = await sync_to_async(User.objects.filter(chat_id=chat_id).exists)()
    
    if user_exists:
        login_url = f"{settings.SITE_BASE_URL}/cargopart/?chat_id={chat_id}&auto_login=true"
        button_text = "🔑 Войти в личный кабинет"
    else:
        login_url = f"{settings.SITE_BASE_URL}/register/?chat_id={chat_id}"
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

# Кнопка для WhatsApp менеджера
async def get_whatsapp_manager_button():
    app_settings = await get_settings()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📲 WhatsApp менеджера", url=app_settings.watapp or "https://default-link.com/")]
        ]
    )
    return keyboard

# Опции для посылок
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
