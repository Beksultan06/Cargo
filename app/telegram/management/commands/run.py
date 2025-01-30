import logging, asyncio, django, os
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from aiogram import Bot, Dispatcher
from app.telegram.management.commands.app.bot import router

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

API_TOKEN = "7446065937:AAF0vetABzvUnhEJXAcN3q_xkNXeUtf6DeM"

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

class Command(BaseCommand):
    help = "Запускает Telegram-бота"

    def handle(self, *args, **kwargs):
        dp.include_router(router)

        async def main():
            try:
                logging.info("Запуск Telegram-бота...")
                await dp.start_polling(bot)
            except Exception as e:
                logging.error(f"Ошибка при запуске бота: {e}")
        asyncio.run(main())