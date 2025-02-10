from aiogram import Router, types
from aiogram.filters import Command
from app.web_app.models import CourierUser, Product, Courier
from django.db import IntegrityError
from asgiref.sync import sync_to_async  # Импортируем sync_to_async для работы с Django ORM в async

router = Router()

# Команда /start для регистрации курьера
@router.message(Command("start"))
async def start_command(message: types.Message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    username = message.from_user.username

    # Сохраняем данные курьера в базе данных с использованием sync_to_async
    try:
        await sync_to_async(CourierUser.objects.get_or_create)(
            chat_id=chat_id,
            defaults={
                'full_name': full_name,
                'username': username
            }
        )
        await message.answer("👋 Привет! Вы зарегистрированы как курьер и будете получать заказы.")
    except IntegrityError:
        await message.answer("✅ Вы уже зарегистрированы как курьер.")
        
@router.callback_query(lambda c: c.data.startswith("accept_order_"))
async def accept_order(callback_query: types.CallbackQuery):
    courier_order_id = int(callback_query.data.split("_")[-1])

    # Получаем заказ из модели Courier
    courier_order = await sync_to_async(Courier.objects.get)(id=courier_order_id)

    # Обновляем статус заказа
    courier_order.status = "Принят курьером"
    await sync_to_async(courier_order.save)()

    await callback_query.answer("✅ Заказ принят и добавлен в систему.")
    await callback_query.message.edit_text(f"🚚 Заказ с трек-номером {courier_order.track.track} принят для доставки.")


@router.callback_query(lambda c: c.data.startswith("reject_order_"))
async def reject_order(callback_query: types.CallbackQuery):
    courier_order_id = int(callback_query.data.split("_")[-1])

    # Обновление статуса заказа на "Отклонён"
    courier_order = await sync_to_async(Courier.objects.get)(id=courier_order_id)
    courier_order.status = "Отклонён курьером"
    await sync_to_async(courier_order.save)()

    await callback_query.answer("❌ Заказ отклонён.")
    await callback_query.message.edit_text(f"⚠️ Заказ с трек-номером {courier_order.track.track} отклонён.")
