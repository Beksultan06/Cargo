from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command('start'))
async def start(message:types.Message):
    await message.answer("Привет это телеграмм бот дла курьеров!")

