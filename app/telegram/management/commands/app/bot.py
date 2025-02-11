from aiogram import types, Router
from aiogram.filters import Command
from django.conf import settings
from app.telegram.management.commands.app.button import get_inline_keyboard, get_main_menu, get_profile_buttons
from aiogram.fsm.context import FSMContext
from app.telegram.management.commands.app.db import get_user_by_chat_id, update_chat_id
from asgiref.sync import sync_to_async
from app.telegram.management.commands.app.states import TrackState
from app.web_app.models import Product, ProductStatus, Settings, User, CourierUser, Courier
from app.telegram.management.commands.run import bot
from django.db import transaction
from django.utils.html import strip_tags
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup
import logging
from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
import aiohttp

# Асинхронная функция для получения настроек
@sync_to_async
def get_settings():
    return Settings.objects.first()


logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("start"))
async def start(message: types.Message):
    chat_id = message.chat.id
    username = message.from_user.username
    full_name = message.from_user.full_name or "Неизвестно"
    logging.info(f"Получен chat_id: {chat_id} от пользователя {username}")

    try:
        # Проверка наличия пользователя в базе данных
        user = await get_user_by_chat_id(chat_id)
        if user:
            # Обновляем chat_id, если он изменился, и показываем главное меню
            await update_chat_id(user, chat_id)
            await message.answer(
                f"✅ Привет, {user.full_name}!\nДобро пожаловать!",
                reply_markup=get_main_menu()
            )
        else:
            # Если пользователь не найден, отправляем кнопку для регистрации
            registration_link = f'{settings.SITE_BASE_URL}/register/?chat_id={chat_id}'
            logging.info(f"Отправляем ссылку регистрации: {registration_link}")
            await message.answer(
                "⚠️ Вы не зарегистрированы.\nПожалуйста, пройдите регистрацию через веб-приложение.",
                reply_markup=await get_inline_keyboard(chat_id=chat_id)
            )
    except Exception as e:
        logging.error(f"Ошибка при обработке пользователя: {e}")
        await message.answer("❌ Произошла ошибка при обработке данных. Попробуйте позже.")

async def notify_registration_success(chat_id, full_name):
    try:
        await bot.send_message(
            chat_id,
            f"✅ Поздравляем, {full_name}! Вы успешно зарегистрированы.\nТеперь вам доступно главное меню.",
            reply_markup=get_main_menu()
        )
    except Exception as e:
        logging.error(f"Ошибка при отправке сообщения о регистрации: {e}")

@router.message(lambda message: message.text == "🧑‍💼 Профиль")
async def send_profile_info(message: types.Message):
    chat_id = message.chat.id
    logging.info(f"Обработка профиля для chat_id: {chat_id}")
    user = await get_user_by_chat_id(chat_id)

    if not user:
        logging.warning(f"Пользователь с chat_id {chat_id} не найден.")
        await message.answer("⚠️ Ваш профиль не найден. Пожалуйста, зарегистрируйтесь.")
        return

    pickup_point_name = user.pickup_point.city if user.pickup_point else "Не указан"
    app_settings = await get_settings()
    text = (
        "📜 *Ваш профиль 📜*\n\n"
        f"🆔 *Персональный ID*: `{user.id_user}`\n"
        f"👤 *ФИО*: {user.full_name}\n"
        f"📞 *Номер*: `{user.phone_number}`\n"
        f"🏡 *Адрес*: {user.address}\n\n"
        f"📍 *ПВЗ*: {pickup_point_name}\n"
        f"📍 *ПВЗ телефон*: [996505180600](tel:996558486448)\n"
        f"📍 *Часы работы*: \n"
        f"📍 *Локация на Карте*: \n\n"
        f"[🌍 LiderCargo (WhatsApp)]({app_settings.watapp})"
    )
    await message.answer(text, parse_mode="Markdown", reply_markup=await get_profile_buttons(chat_id))


@router.message(lambda message: message.text == "🚫 Запрещенные товары")
async def forbidden_goods(message: types.Message):
    settings = await Settings.objects.afirst()
    text = strip_tags(settings.prohibited_goods) if settings and settings.prohibited_goods else "⚠️ Информация отсутствует."
    await message.answer(text, parse_mode="Markdown")

@router.message(lambda message: message.text == "📕 Инструкция")
async def send_instruction(message: types.Message):
    settings = await Settings.objects.afirst()
    text = strip_tags(settings.instructions) if settings and settings.instructions else "⚠️ Информация отсутствует."
    await message.answer(text, parse_mode="Markdown")

@router.message(lambda message: message.text == "ℹ️ О нас")
async def send_about_info(message: types.Message):
    settings = await Settings.objects.afirst()
    text = strip_tags(settings.about) if settings and settings.about else "⚠️ Информация отсутствует."
    await message.answer(text, parse_mode="Markdown")

@router.message(lambda message: message.text == "📍 Адреса")
async def show_address(message: types.Message):
    settings = await sync_to_async(lambda: Settings.objects.first())()
    user = await sync_to_async(lambda: User.objects.get(chat_id=message.chat.id))()

    if not settings or not user.id_user:
        await message.answer("❌ Ошибка: Адрес склада пока не указан.")
        return

    # Формируем текст адреса
    address_text = f"{settings.address} {user.id_user}\n{settings.phone}"
    
    # Функция для экранирования символов Markdown
    import re
    def escape_markdown(text):
        return re.sub(r'([\_\*\[\]\(\)\~\`\>\#\+\-\=\|\{\}\.\!])', r'\\\1', text)

    # Экранируем текст
    escaped_address_text = escape_markdown(address_text)

    # Сохраняем адрес в поле address_tg_bot, если он отличается
    if settings.address_tg_bot != address_text:
        await sync_to_async(lambda: Settings.objects.filter(pk=settings.pk).update(address_tg_bot=address_text))()

    # Отправляем адрес пользователю
    await message.answer(f"📍 *Адрес склада:* \n\n`{escaped_address_text}`", parse_mode="MarkdownV2")

    # Дополнительная информация о складе
    info_text = (
        f"📩 Информация о складе в Кыргызстане 🇰🇬:\n\n"
        f"⚠ Чтобы ваши посылки не потерялись, отправьте скрин заполненного адреса и получите подтверждение от менеджера.\n\n"
        f"❗️❗️❗️ Только после подтверждения ✅ адреса Карго несет ответственность за ваши посылки 📦"
        f"\n\n📞 {settings.phone}"
    )

    if settings.watapp:
        info_text += f"\n🔗 WhatsApp менеджера: {settings.watapp}"

    # Добавляем кнопку WhatsApp, если указан
    keyboard = None
    if settings.watapp:
        keyboard = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="WhatsApp менеджера", url=settings.watapp)]
            ]
        )

    # Отправляем информацию о складе
    await message.answer(info_text, reply_markup=keyboard)



@router.message(lambda message: message.text == "⚙️ Поддержка")
async def send_about_info(message: types.Message):
    settings = await Settings.objects.afirst()
    text = strip_tags(settings.support) if settings and settings.support else "⚠️ Информация отсутствует."
    await message.answer(text, parse_mode="Markdown")

@router.message(lambda message: message.text == "✅ Добавить трек")
async def start_add_track(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )
    await message.answer("✏️ Введите ваш трек-номер:", reply_markup=keyboard)
    await state.set_state(TrackState.waiting_for_track)

@router.message(lambda message: message.text == "🔙 Назад")
async def cancel_add_track(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Добавить трек")]
        ],
        resize_keyboard=True
    )
    await state.clear()
    await message.answer("🚫 Добавление трека отменено.", reply_markup=get_main_menu())

@router.message(TrackState.waiting_for_track)
async def save_track(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    track_number = message.text.strip()
    if len(track_number) < 5:
        await message.answer("❌ Ошибка: Трек-номер слишком короткий. Попробуйте снова.")
        return
    user = await sync_to_async(lambda: User.objects.filter(chat_id=chat_id).first())()
    if not user:
        await message.answer("❌ Ошибка: Вы не зарегистрированы.")
        await state.clear()
        return
    existing_product = await sync_to_async(lambda: Product.objects.filter(track=track_number).first())()
    if existing_product:
        await message.answer(f"⚠️ Этот трек-номер уже добавлен!\n\nСтатус: {existing_product.get_status_display()}")
        await state.clear()
        return
    def create_product():
        with transaction.atomic():
            product = Product.objects.create(
                user=user,
                track=track_number,
                status=ProductStatus.WAITING_FOR_ARRIVAL
            )
            return product
    product = await sync_to_async(create_product)()
    await message.answer(
        f"✅ Трек-номер **{track_number}** добавлен!\nСтатус: {product.get_status_display()}",
        reply_markup=get_main_menu()
    )
    await state.clear()

@router.message(lambda message: message.text == "📦 Мои посылки")
async def show_my_packages(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    user = await sync_to_async(lambda: User.objects.filter(chat_id=chat_id).first())()
    if not user:
        await message.answer("❌ Ошибка: Вы не зарегистрированы.")
        return
    user_products = await sync_to_async(lambda: list(Product.objects.filter(user=user)))()
    if not user_products:
        await message.answer("📭 У вас пока нет посылок.", reply_markup=get_main_menu())
        return
    text = "📦 Ваши посылки:\n\n"
    for product in user_products:
        text += f"🔹 **Трек:** `{product.track}`\n"
        text += f"📍 **Статус:** {product.get_status_display()}\n"
        text += "➖➖➖➖➖➖➖➖➖➖\n"
    await message.answer(text, reply_markup=get_main_menu(), parse_mode="Markdown")


# Токен второго бота (бота курьера)
SECOND_BOT_TOKEN = '7143865311:AAGLTrlaZ5Ko5AR8M3QOhSNf2vnqiZ-5-XM'

async def send_telegram_message(chat_id, product):
    message = (
        f"📦 Ваш товар с трек-номером {product.track} прибыл в офис!\n"
        f"Вес: {product.weight} кг.\n"
        f"Выберите удобный способ получения:"
    )

    # Создание инлайн-клавиатуры
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🏢 Забрать в офисе", callback_data=f"pickup_office_{product.id}"),
            InlineKeyboardButton(text="🚚 Доставить курьером", callback_data=f"deliver_courier_{product.id}")
        ]
    ])

    try:
        await bot.send_message(chat_id, message, reply_markup=keyboard)
    except Exception as e:
        pass
# Состояния FSM для получения адреса и телефона
class DeliveryState(StatesGroup):
    waiting_for_address = State()
    waiting_for_phone = State()

# Обработка кнопки "Доставить курьером"
@router.callback_query(lambda c: c.data.startswith("deliver_courier_"))
async def handle_deliver_courier(callback_query: types.CallbackQuery, state: FSMContext):
    product_id = int(callback_query.data.split("_")[-1])

    await state.update_data(product_id=product_id)
    await callback_query.message.answer("📍 Пожалуйста, введите адрес доставки.")
    await state.set_state(DeliveryState.waiting_for_address)

# Получение адреса
@router.message(DeliveryState.waiting_for_address)
async def process_address(message: types.Message, state: FSMContext):
    address = message.text
    await state.update_data(address=address)

    await message.answer("📞 Теперь отправьте ваш номер телефона.")
    await state.set_state(DeliveryState.waiting_for_phone)
@router.message(DeliveryState.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text
    await state.update_data(phone=phone)

    data = await state.get_data()
    product_id = data.get("product_id")
    address = data.get("address")

    # Получаем продукт с привязанным пользователем
    product = await sync_to_async(Product.objects.select_related('user').get)(id=product_id)

    # Получаем пользователя через sync_to_async
    user = await sync_to_async(lambda: product.user)()

    # Сохраняем заказ в модель Courier
    courier_order = await sync_to_async(Courier.objects.create)(
        user=user,
        track=product,
        address=address,
        phone=phone,
        # price=product.price,
        type_payment="Наличный",
        status="Ожидает подтверждения курьером"
    )

    # Отправляем заказ курьеру
    await send_order_to_courier_bot(courier_order.id, product.track, address, phone, product.price)

    await message.answer("🚚 Ваш заказ отправлен курьеру. Ожидайте подтверждения.")
    await state.clear()

async def send_order_to_courier_bot(courier_order_id, track, address, phone, price):
    couriers = await sync_to_async(list)(CourierUser.objects.all())
    
    if not couriers:
        return

    # Форматируем цену с двумя знаками после запятой
    formatted_price = f"{price:.2f}$"

    message = (
        f"🚚 *Новый заказ на доставку!*\n"
        f"📦 Трек-номер: {track}\n"
        f"📍 Адрес: {address}\n"
        f"📞 Телефон: {phone}\n"
        f"💰 Сумма к оплате: *{formatted_price}*\n\n"
        f"Нажмите кнопку ниже, чтобы принять заказ."
    )


    keyboard_dict = {
        "inline_keyboard": [
            [
                {"text": "✅ Принять заказ", "callback_data": f"accept_order_{courier_order_id}"},
                {"text": "❌ Отклонить заказ", "callback_data": f"reject_order_{courier_order_id}"}
            ]
        ]
    }

    async with aiohttp.ClientSession() as session:
        for courier in couriers:
            payload = {
                "chat_id": courier.chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "reply_markup": keyboard_dict
            }
            url = f"https://api.telegram.org/bot{SECOND_BOT_TOKEN}/sendMessage"

            try:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        pass
                    else:
                        error_response = await response.text()
            except Exception as e:
                pass
