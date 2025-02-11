import asyncio
import os
from dotenv import load_dotenv
from django.core.management.base import BaseCommand
from aiogram import Dispatcher
from app.telegram.management.commands.bot_instance import bot, bot_cuorier

load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

dp = Dispatcher()
dp_cuorier = Dispatcher()

class Command(BaseCommand):
    help = "Запускает Telegram-бота"

    def handle(self, *args, **kwargs):
        from app.telegram.management.commands.app.bot import router as cklient
        from app.telegram.management.commands.app.courier import router as courier # Добавьте роутер для курьерского бота

        # Подключаем роутеры к соответствующим диспетчерам
        dp.include_router(cklient)
        dp_cuorier.include_router(courier)

        async def main():
            try:
                await bot.delete_webhook(drop_pending_updates=True)
                await bot_cuorier.delete_webhook(drop_pending_updates=True)
                bot_task = asyncio.create_task(dp.start_polling(bot))
                courier_task = asyncio.create_task(dp_cuorier.start_polling(bot_cuorier))
                await asyncio.gather(bot_task, courier_task)
            except Exception as e:
                pass
        asyncio.run(main())