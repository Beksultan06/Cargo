from aiogram import types, Router
from aiogram.filters import Command
from django.conf import settings
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

    logging.info(f"Получен chat_id: {chat_id} от пользователя {username}")

    if not username:
        await message.answer(
            "❌ У вас отсутствует username в Telegram.\nПожалуйста, установите его в настройках и повторите попытку."
        )
        return

    try:
        user = await sync_to_async(lambda: User.objects.filter(username=username).first())()

        if user:
            if user.chat_id != chat_id:
                await sync_to_async(lambda: User.objects.filter(username=username).update(chat_id=chat_id))()
                await message.answer(
                    f"✅ Привет, {user.full_name}!\nВаш chat_id обновлен.",
                    reply_markup=get_inline_keyboard()
                )
            else:
                await message.answer(
                    f"✅ Привет, {user.full_name}!\nВы уже зарегистрированы.",
                    reply_markup=get_inline_keyboard()
                )
        else:
            registration_link = f'{settings.SITE_BASE_URL}/register/?chat_id={chat_id}'
            logging.info(f"Отправляем ссылку регистрации: {registration_link}")
            await message.answer(
                "⚠️ Вы не зарегистрированы.\nПожалуйста, пройдите регистрацию через веб-приложение.",
                reply_markup=get_inline_keyboard(registration=True, chat_id=chat_id)
            )
    except Exception as e:
        logging.error(f"Ошибка при обработке пользователя: {e}")
        await message.answer("❌ Произошла ошибка при обработке данных. Попробуйте позже.",
                             reply_markup=get_inline_keyboard(registration=True, chat_id=chat_id))

