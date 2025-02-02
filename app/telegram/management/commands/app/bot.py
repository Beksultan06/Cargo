from aiogram import types, Router
from aiogram.filters import Command
from django.conf import settings
from app.telegram.management.commands.app.button import get_inline_keyboard, get_main_menu, get_profile_buttons,\
get_support_buttons, get_whatsapp_manager_button
import logging
from app.telegram.management.commands.app.db import get_user_by_chat_id, update_chat_id

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    chat_id = message.chat.id
    username = message.from_user.username
    full_name = message.from_user.full_name or "Неизвестно"
    logging.info(f"Получен chat_id: {chat_id} от пользователя {username}")
    try:
        user = await get_user_by_chat_id(chat_id)
        if user:
            await update_chat_id(user, chat_id)
            await message.answer(
                f"✅ Привет, {user.full_name}!\nДобро пожаловать!",
                reply_markup=get_main_menu()
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
        await message.answer("❌ Произошла ошибка при обработке данных. Попробуйте позже.")

@router.message(lambda message: message.text == "🚫 Запрещенные товары")
async def forbidden_goods(message: types.Message):
    text = (
        "📢 *Список запрещенных к перевозке грузов* ❗\n\n"
        "🔴 *Лекарственные препараты, наркотические, психотропные вещества*;\n"
        "🔴 *Легковоспламеняющиеся, взрывчатые, едкие вещества* (фейерверки, различные газы в баллонах и т.д.);\n"
        "🔴 *Острые, колющие, режущие предметы*;\n"
        "🔴 *Оружие, имитация оружия*;\n"
        "🔴 *Предметы военного характера*;\n"
        "🔴 *Жидкие, сыпучие, порошковые, густые вещества*;\n"
        "🔴 *Электронные сигареты*;\n\n"
        "📌 Если у вас возникают сомнения относительно заказа какого-либо товара, *лучше напишите нам*, "
        "и мы предоставим информацию о возможности его доставки.\n\n"
        "⚠️ Эти товары запрещены для перевозки в соответствии с актами таможенных правил. "
        "В случае заказа указанных товаров, *налагается штраф в размере 10-50 тысяч сом*."
    )
    await message.answer(text, parse_mode="Markdown")

@router.message(lambda message: message.text == "⚙️ Поддержка")
async def support_info(message: types.Message):
    text = (
        "📩 *Если у вас есть вопросы? Напишите нам*\n\n"
        "📍 *ПВЗ*: Ош\n"
        "📍 *ПВЗ телефон*: [996505180600](tel:996558486448)\n"
        "📍 *Часы работы*: \n"
        "📍 *Локация на Карте*: \n\n"
        "[🌍 LiderCargo (WhatsApp)](https://wa.me/996505180600)"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=get_support_buttons())

@router.message(lambda message: message.text == "📍 Адреса")
async def send_address_info(message: types.Message):
    text = (
        "📩 *Скопируйте ниже. Это адрес склада в Китае 🇨🇳:*\n\n"
        "🟢 *АКБ-1452*\n"
        "🟢 *17633321256*\n"
        "🟢 *Гуандун, Фошань, Наньхай, Яхуа Логистик*\n\n"
        "📢 Чтобы ваши посылки не потерялись, обязательно отправьте скрин *заполненного адреса* "
        "и получите *подтверждение* от нашего менеджера.\n\n"
        "🔹 📞 [996504546999](tel:996504546999)\n\n"
        "‼️‼️ *Только после подтверждения ✅ адреса Карго несет ответственность за ваши посылки 📦*"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=get_whatsapp_manager_button())

@router.message(lambda message: message.text == "🧑‍💼 Профиль")
async def send_profile_info(message: types.Message):
    chat_id = message.chat.id
    user = await get_user_by_chat_id(chat_id)
    if not user:
        await message.answer("⚠️ Ваш профиль не найден. Пожалуйста, зарегистрируйтесь.")
        return
    pickup_point_name = user.pickup_point.city if user.pickup_point else "Не указан"
    text = (
        "📜 *Ваш профиль 📜*\n\n"
        f"🆔 *Персональный ID*: `{user.id_user}`\n"
        f"👤 *ФИО*: {user.full_name}\n"
        f"📞 *Номер*: `{user.phone_number}`\n"
        f"🏡 *Адрес*: {user.address}\n\n"
        f"📍 *ПВЗ*: {pickup_point_name}\n"
        f"📍 *ПВЗ телефон*:  [996505180600](tel:996558486448)\n"
        "📍 *Часы работы*: \n"
        "📍 *Локация на Карте*: \n\n"
        "[🌍 LiderCargo (WhatsApp)](https://www.youtube.com/)"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=get_profile_buttons(chat_id))