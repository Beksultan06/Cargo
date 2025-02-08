from aiogram import Router, types
from aiogram.filters import Command
from app.web_app.models import ProductStatus, Settings
from django.utils.html import strip_tags
from app.telegram.management.commands.app.button import get_profile_courier
from app.telegram.management.commands.bot_instance import bot_cuorier
from aiogram.types import CallbackQuery
from app.web_app.models import Product  # Импортируем модель
from asgiref.sync import sync_to_async

router = Router()

@router.message(Command('start'))
async def start(message:types.Message):
    await message.answer("Привет это телеграмм бот дла курьеров!", reply_markup=get_profile_courier())

@router.message(lambda message: message.text == "📕 Инструкция")
async def send_instruction(message: types.Message):
    settings = await Settings.objects.afirst()
    text = strip_tags(settings.instructions) if settings and settings.instructions else "⚠️ Информация отсутствует."
    await message.answer(text, parse_mode="Markdown")

@router.message(lambda message: message.text == "⚙️ Поддержка")
async def send_about_info(message: types.Message):
    settings = await Settings.objects.afirst()
    text = strip_tags(settings.support) if settings and settings.support else "⚠️ Информация отсутствует."
    await message.answer(text, parse_mode="Markdown")

@router.message(lambda message: message.text == "ℹ️ О нас")
async def send_about_info(message: types.Message):
    settings = await Settings.objects.afirst()
    text = strip_tags(settings.about) if settings and settings.about else "⚠️ Информация отсутствует."
    await message.answer(text, parse_mode="Markdown")

async def send_telegram_message_cuorier(chat_id, message, track_number):
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="✅ Принять", callback_data=f"accept_{track_number}")]
        ]
    )
    await bot_cuorier.send_message(chat_id, message, reply_markup=keyboard)

@router.callback_query(lambda c: c.data.startswith('accept_'))
async def handle_accept_callback(callback_query: CallbackQuery):
    track_number = callback_query.data.split('_')[1]
    product = await sync_to_async(Product.objects.filter(track=track_number).first)()
    if product:
        product.status = ProductStatus.COURIER_IN_TRANSIT
        await sync_to_async(product.save)()

        await callback_query.answer("📦 Посылка принята и передана курьеру!", show_alert=True)
        await callback_query.message.edit_text(
            f"📦 Посылка с трек-номером {track_number} принята и передана курьеру! 🚚"
        )
    else:
        await callback_query.answer("❌ Посылка не найдена!", show_alert=True)