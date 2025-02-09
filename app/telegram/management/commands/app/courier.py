from aiogram import Router, types
from aiogram.filters import Command
from app.web_app.models import Settings
from django.utils.html import strip_tags
from app.telegram.management.commands.app.button import get_profile_courier

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