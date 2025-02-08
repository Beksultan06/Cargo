import logging
import asyncio
import os
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from aiogram import Dispatcher
from app.telegram.management.commands.bot_instance import bot

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Удаляем повторный вызов django.setup(), чтобы избежать ошибки повторной инициализации
# django.setup()

dp = Dispatcher()

class Command(BaseCommand):
    help = "Запускает Telegram-бота"

    def handle(self, *args, **kwargs):
        from app.telegram.management.commands.app.bot import router

        dp.include_router(router)

        async def main():
            try:
                logging.info("\ud83d\ude80 Запуск Telegram-бота...")
                await bot.delete_webhook(drop_pending_updates=True)
                await dp.start_polling(bot)
            except Exception as e:
                logging.error(f"\u274c Ошибка при запуске бота: {e}")

        asyncio.run(main())