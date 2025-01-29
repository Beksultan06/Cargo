from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from django.conf import settings

def get_inline_keyboard(registration=False, chat_id=None):
    buttons = [
        [InlineKeyboardButton(text="💬 Написать менеджеру", url="https://www.youtube.com/")]
    ]

    if registration and chat_id:
        registration_url = f"{settings.SITE_BASE_URL}/?chat_id={chat_id}".strip()
        buttons.append([
            InlineKeyboardButton(
                text='📝 Пройти регистрацию',
                web_app=WebAppInfo(url=registration_url)
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
