from aiogram import types, Router
from aiogram.filters import Command
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from app.telegram.management.commands.app.button import get_inline_keyboard
import logging

router = Router()
User = get_user_model()

@router.message(Command("start"))
async def start(message: types.Message):
    chat_id = message.chat.id
    username = message.from_user.username
    full_name = message.from_user.full_name or "Неизвестно"

    if username is None:
        await message.answer(
            "У вас отсутствует username в Telegram. Пожалуйста, установите его в настройках и повторите попытку."
        )
        return

    try:
        user = await sync_to_async(lambda: User.objects.filter(username=username).first())()

        if user:
            if user.chat_id != chat_id:
                user.chat_id = chat_id
                await sync_to_async(user.save)()
                await message.answer(f"Привет, {user.full_name}! Ваш chat_id обновлен.", reply_markup=get_inline_keyboard(chat_id))
            else:
                await message.answer(f"Привет, {user.full_name}! Ваш chat_id уже сохранен.", reply_markup=get_inline_keyboard(chat_id))
        else:
            await message.answer(
                "Вы не зарегистрированы. Пожалуйста, пройдите регистрацию через веб-приложение.",
                reply_markup=get_inline_keyboard(chat_id)
            )
    except Exception as e:
        await message.answer("Произошла ошибка при обработке данных. Попробуйте позже.")
        logging.error(f"Ошибка: {e}")