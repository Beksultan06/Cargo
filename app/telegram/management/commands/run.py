import logging
import asyncio
import django
import os
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from aiogram import Dispatcher
from app.telegram.management.commands.bot_instance import bot
from app.telegram.management.commands.app.bot import router

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

dp = Dispatcher()

class Command(BaseCommand):
    help = "Запускает Telegram-бота"

    def handle(self, *args, **kwargs):
        dp.include_router(router)

        async def main():
            try:
                logging.info("🚀 Запуск Telegram-бота...")
                await bot.delete_webhook(drop_pending_updates=True)
                await dp.start_polling(bot)
            except Exception as e:
                logging.error(f"❌ Ошибка при запуске бота: {e}")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
