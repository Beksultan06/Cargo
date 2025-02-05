from aiogram import types, Router
from aiogram.filters import Command
from django.conf import settings
from app.telegram.management.commands.app.button import get_inline_keyboard, get_main_menu, get_profile_buttons
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from app.telegram.management.commands.app.db import get_user_by_chat_id, update_chat_id
from asgiref.sync import sync_to_async
from app.telegram.management.commands.app.states import TrackState
from app.web_app.models import Product, ProductStatus, Settings, User
from app.telegram.management.commands.run import bot
from django.db import transaction
import logging

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
            return

        registration_link = f'{settings.SITE_BASE_URL}/?chat_id={chat_id}'
        logging.info(f"Отправляем ссылку регистрации: {registration_link}")
        await message.answer(
            "⚠️ Вы не зарегистрированы.\nПожалуйста, пройдите регистрацию через веб-приложение.",
            reply_markup=get_inline_keyboard(registration=True, chat_id=chat_id)
        )
    except Exception as e:
        logging.error(f"Ошибка при обработке пользователя: {e}")
        await message.answer("❌ Произошла ошибка при обработке данных. Попробуйте позже.")

async def notify_registration_success(chat_id, full_name):
    try:
        await bot.send_message(
            chat_id,
            f"✅ Поздравляем, {full_name}! Вы успешно зарегистрированы.\nТеперь вам доступно главное меню.",
            reply_markup=get_main_menu()
        )
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения о регистрации: {e}")

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

from django.utils.html import strip_tags

@router.message(lambda message: message.text == "🚫 Запрещенные товары")
async def forbidden_goods(message: types.Message):
    settings = await Settings.objects.afirst()
    text = strip_tags(settings.prohibited_goods) if settings and settings.prohibited_goods else "⚠️ Информация отсутствует."
    await message.answer(text, parse_mode="Markdown")

@router.message(lambda message: message.text == "📕 Инструкция")
async def send_instruction(message: types.Message):
    settings = await Settings.objects.afirst()
    text = strip_tags(settings.instructions) if settings and settings.instructions else "⚠️ Информация отсутствует."
    await message.answer(text, parse_mode="Markdown")

@router.message(lambda message: message.text == "ℹ️ О нас")
async def send_about_info(message: types.Message):
    settings = await Settings.objects.afirst()
    text = strip_tags(settings.about) if settings and settings.about else "⚠️ Информация отсутствует."
    await message.answer(text, parse_mode="Markdown")

@router.message(lambda message: message.text == "📍 Адреса")
async def send_about_info(message: types.Message):
    settings = await Settings.objects.afirst()
    text = strip_tags(settings.about) if settings and settings.about else "⚠️ Информация отсутствует."
    await message.answer(text, parse_mode="Markdown")

@router.message(lambda message: message.text == "⚙️ Поддержка")
async def send_about_info(message: types.Message):
    settings = await Settings.objects.afirst()
    text = strip_tags(settings.support) if settings and settings.support else "⚠️ Информация отсутствует."
    await message.answer(text, parse_mode="Markdown")

@router.message(lambda message: message.text == "✅ Добавить трек")
async def start_add_track(message: types.Message, state: FSMContext):
    await message.answer("✏️ Введите ваш трек-номер:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(TrackState.waiting_for_track)

@router.message(TrackState.waiting_for_track)
async def save_track(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    track_number = message.text.strip()

    if len(track_number) < 5:
        await message.answer("❌ Ошибка: Трек-номер слишком короткий. Попробуйте снова.")
        return
    user = await sync_to_async(lambda: User.objects.filter(chat_id=chat_id).first())()
    if not user:
        await message.answer("❌ Ошибка: Вы не зарегистрированы.")
        await state.clear()
        return
    existing_product = await sync_to_async(lambda: Product.objects.filter(track=track_number).first())()
    if existing_product:
        await message.answer(f"⚠️ Этот трек-номер уже добавлен!\n\nСтатус: {existing_product.get_status_display()}")
        await state.clear()
        return
    def create_product():
        with transaction.atomic():
            product = Product.objects.create(
                user=user,
                track=track_number,
                status=ProductStatus.WAITING_FOR_ARRIVAL
            )
            return product
    product = await sync_to_async(create_product)()
    await message.answer(
        f"✅ Трек-номер **{track_number}** добавлен!\nСтатус: {product.get_status_display()}",
        reply_markup=get_main_menu()
    )
    await state.clear()

@router.message(lambda message: message.text == "📦 Мои посылки")
async def show_my_packages(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    user = await sync_to_async(lambda: User.objects.filter(chat_id=chat_id).first())()
    if not user:
        await message.answer("❌ Ошибка: Вы не зарегистрированы.")
        return
    user_products = await sync_to_async(lambda: list(Product.objects.filter(user=user)))()

    if not user_products:
        await message.answer("📭 У вас пока нет посылок.", reply_markup=get_main_menu())
        return
    text = "📦 Ваши посылки:\n\n"
    for product in user_products:
        text += f"🔹 **Трек:** `{product.track}`\n"
        text += f"📍 **Статус:** {product.get_status_display()}\n"
        text += "➖➖➖➖➖➖➖➖➖➖\n"

    await message.answer(text, reply_markup=get_main_menu(), parse_mode="Markdown")