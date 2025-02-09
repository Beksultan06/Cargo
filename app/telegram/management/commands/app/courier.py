from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from asgiref.sync import sync_to_async
from app.web_app.models import Settings, Product, Courier, User
from app.telegram.management.commands.bot_instance import bot_cuorier
from app.telegram.management.commands.app.button import get_profile_courier
from app.telegram.management.commands.app.states import CourierOrderStates
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command('start'))
async def start(message: types.Message):
    await message.answer("Привет это телеграмм бот для курьеров!", reply_markup=get_profile_courier())

@router.message(lambda message: message.text == "📕Инструкция")
async def send_instruction(message: types.Message):
    settings = await Settings.objects.afirst()
    text = strip_tags(settings.instructions) if settings and settings.instructions else "⚠️ Информация отсутствует."
    await message.answer(text, parse_mode="Markdown")

@router.message(lambda message: message.text == "⚙️ Поддержка")
async def send_support_info(message: types.Message):
    settings = await Settings.objects.afirst()
    text = strip_tags(settings.support) if settings and settings.support else "⚠️ Информация отсутствует."
    await message.answer(text, parse_mode="Markdown")

@router.message(lambda message: message.text == "ℹ️ О нас")
async def send_about_info(message: types.Message):
    settings = await Settings.objects.afirst()
    text = strip_tags(settings.about) if settings and settings.about else "⚠️ Информация отсутствует."
    await message.answer(text, parse_mode="Markdown")

@router.message(CourierOrderStates.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text
    data = await state.get_data()
    track_number = data.get('track_number')
    address = data.get('address')

    try:
        # Получаем продукт по трек-номеру
        product = await sync_to_async(Product.objects.get)(track=track_number)
        # Получаем пользователя по chat_id
        user = await sync_to_async(User.objects.get)(chat_id=message.from_user.id)
        
        # Проверка данных перед сохранением
        logger.info(f"Создание доставки: Пользователь={user.full_name}, Трек={product.track}, Адрес={address}, Телефон={phone}")

        # Создаем запись о доставке в базе данных
        await sync_to_async(Courier.objects.create)(
            user=user,
            track=product,
            address=address,
            phone=phone,
            type_payment='Наличный'
        )
        logger.info(f"Доставка успешно сохранена для трека: {track_number}")

        # Формируем сообщение для курьеров
        courier_message = (
            f"✅ Доставка оформлена!\n\n"
            f"📍 Пользователь: {user.full_name} ({user.pickup_point})\n"
            f"📦 Трек номер: {product.track} - {product.get_status_display()} - {product.price}$\n"
            f"📍 Адрес: {address}\n"
            f"📞 Телефон: {phone}"
        )

        # Получаем всех курьеров и отправляем сообщение каждому
        couriers = await sync_to_async(User.objects.filter)(is_courier=True)
        for courier in await sync_to_async(list)(couriers):
            if courier.chat_id:
                logger.info(f"Отправка сообщения курьеру {courier.full_name} (chat_id={courier.chat_id})")
                await bot_cuorier.send_message(courier.chat_id, courier_message)

        # Обновляем статус продукта
        product.status = 'courier_on_the_way'
        await sync_to_async(product.save)()
        logger.info(f"Статус продукта {product.track} обновлен на 'courier_on_the_way'")

        # Уведомление пользователю
        await bot_cuorier.send_message(user.chat_id, f"🚚 Ваша доставка в пути! Курьер свяжется с вами скоро.")
        await state.clear()

    except Exception as e:
        logger.error(f"Ошибка при обработке доставки: {e}")
        await message.answer("⚠️ Произошла ошибка при оформлении доставки. Пожалуйста, попробуйте позже.")
