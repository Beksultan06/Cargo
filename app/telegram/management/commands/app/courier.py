from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from asgiref.sync import sync_to_async
from django.db import IntegrityError

from app.web_app.models import CourierUser, Product, Courier, ProductStatus

router = Router()

# Команда /start для регистрации курьера
@router.message(Command("start"))
async def start_command(message: types.Message):
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    username = message.from_user.username

    try:
        await sync_to_async(CourierUser.objects.get_or_create)(
            chat_id=chat_id,
            defaults={'full_name': full_name, 'username': username}
        )
        await message.answer("👋 Привет! Вы зарегистрированы как курьер и будете получать заказы.")
    except IntegrityError:
        await message.answer("✅ Вы уже зарегистрированы как курьер.")

# Универсальная функция для обновления статусов заказа и товара
async def update_order_and_product_status(courier_order_id, courier_status, product_status):
    courier_order = await sync_to_async(Courier.objects.select_related('track').get)(id=courier_order_id)
    product = courier_order.track

    courier_order.status = courier_status
    await sync_to_async(courier_order.save)()

    product.status = product_status
    await sync_to_async(product.save)()

    return courier_order, product

# Принятие заказа
@router.callback_query(lambda c: c.data.startswith("accept_order_"))
async def accept_order(callback_query: types.CallbackQuery):
    courier_order_id = int(callback_query.data.split("_")[-1])

    await update_order_and_product_status(
        courier_order_id,
        courier_status="Принят курьером",
        product_status=ProductStatus.COURIER_IN_TRANSIT
    )

    # Меняем только кнопки на "Завершить заказ"
    complete_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Завершить заказ", callback_data=f"complete_order_{courier_order_id}")]
    ])

    await callback_query.answer("✅ Заказ принят и товар отправлен в путь.")
    await callback_query.message.edit_reply_markup(reply_markup=complete_keyboard)

# Завершение заказа и изменение текста
@router.callback_query(lambda c: c.data.startswith("complete_order_"))
async def complete_order(callback_query: types.CallbackQuery):
    courier_order_id = int(callback_query.data.split("_")[-1])

    courier_order, product = await update_order_and_product_status(
        courier_order_id,
        courier_status="Завершён",
        product_status=ProductStatus.COMPLETED
    )

    # Обновляем текст сообщения на финальный статус и убираем кнопки
    await callback_query.answer("✅ Заказ завершён.")
    await callback_query.message.edit_text(
        f"🎉 Заказ успешно закончен на сумму {product.price}$.\n"
        f"Спасибо за выполнение заказа! 🚚"
    )
