from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from django.conf import settings

def get_inline_keyboard(registration=False):
    buttons = [
        [InlineKeyboardButton(text="💬 Написать менеджеру", url="https://www.youtube.com/")]
    ]

    if registration:
        buttons.append([
            InlineKeyboardButton(
                text='📝 Пройти регистрацию',
                web_app=WebAppInfo(url=f'{settings.SITE_BASE_URL}')
            )
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
