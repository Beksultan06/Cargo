import logging, json, re
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from app.telegram.management.commands.app.bot import notify_registration_success
from app.web_app.models import User, Pvz, Product
from app.web_app.pagination import paginate_queryset
from .models import ProductStatus, Settings, User, Pvz, Product, generate_code_from_pvz
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from app.web_app.forms import TrackingSearchForm
from django.utils.decorators import method_decorator
from django.views import View
from django.middleware.csrf import get_token
from app.telegram.management.commands.bot_instance import bot
from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async
import asyncio
from app.telegram.management.commands.app.bot import send_telegram_message

logger = logging.getLogger(__name__)

def register(request):
    chat_id = request.GET.get('chat_id') or request.POST.get('chat_id')
    logging.info(f"Полученный chat_id в register: {chat_id}")
    if chat_id:
        user = User.objects.filter(chat_id=chat_id).first()
        if user:
            messages.info(request, '✅ Вы уже зарегистрированы.')
            return redirect('cargopart')
    if request.method == 'POST':
        full_name = request.POST.get('fullName', '').strip()
        phone = request.POST.get('phone', '').strip()
        pvz_id = request.POST.get('pvz')
        address = request.POST.get('address', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirmPassword', '').strip()
        if not full_name or not phone or not pvz_id or not address or not password or not confirm_password:
            messages.error(request, '❌ Все поля обязательны для заполнения.')
            return render(request, 'index.html', {'pvz_list': Pvz.objects.all()})
        if password != confirm_password:
            messages.error(request, '❌ Пароли не совпадают.')
            return render(request, 'index.html', {'pvz_list': Pvz.objects.all()})
        try:
            pvz = Pvz.objects.get(id=pvz_id)
        except Pvz.DoesNotExist:
            messages.error(request, '❌ Выбранный ПВЗ не существует.')
            return render(request, 'index.html', {'pvz_list': Pvz.objects.all()})
        if User.objects.filter(phone_number=phone).exists():
            messages.error(request, '❌ Пользователь с таким номером телефона уже зарегистрирован.')
            return render(request, 'index.html', {'pvz_list': Pvz.objects.all()})
        try:
            new_user = User.objects.create(
                full_name=full_name,
                phone_number=phone,
                pickup_point=pvz,
                address=address,
                username=phone,
                password=make_password(password),
                chat_id=chat_id
            )
            logging.info(f"Создан новый пользователь {new_user.username} с chat_id: {new_user.chat_id}")
            user = authenticate(request, username=phone, password=password)
            if user:
                login(request, user)
                async_to_sync(notify_registration_success)(chat_id, full_name)
                messages.success(request, '✅ Регистрация и авторизация прошли успешно!')
                async_to_sync(notify_registration_success)(chat_id, full_name)
                return redirect('cargopart')
        except Exception as e:
            logging.error(f"Ошибка при регистрации: {e}")
            messages.error(request, f'❌ Ошибка при регистрации: {e}')
            return render(request, 'index.html', {'pvz_list': Pvz.objects.all()})
    return render(request, 'index.html', {'pvz_list': Pvz.objects.all()})

def login_view(request):
    if request.method == "POST":
        phone_number = request.POST.get("phone", "").strip().replace(" ", "").replace("-", "")
        password = request.POST.get("password", "").strip()
        phone_number = "+996" + phone_number[-9:]
        if not re.match(r"^\+996\d{9}$", phone_number):
            return JsonResponse({"status": "error", "message": "Введите корректный номер в формате +996 XXX XXX XXX"}, status=400)
        user = authenticate(request, phone_number=phone_number, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"status": "success", "redirect_url": "/cargopart/"})
        else:
            return JsonResponse({"status": "error", "message": "Неверный номер телефона или пароль"}, status=400)
    csrf_token = get_token(request)
    return render(request, "enter.html", {"csrf_token": csrf_token})

@login_required(login_url='/')
def cargopart(request):
    user = request.user

    if request.method == "POST":
        print("📩 Форма отправлена!")
        print("📨 request.POST:", request.POST)

        full_name = request.POST.get("full_name", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        pvz_id = request.POST.get("pickup_point", "").strip()
        warehouse_address = request.POST.get("warehouse_address", "").strip()
        password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get("confirm-password", "").strip()
        logger.info(f"POST data: password={password}, confirm_password={confirm_password}")

        pvz = None
        if pvz_id:
            try:
                pvz = Pvz.objects.get(id=int(pvz_id))
            except (Pvz.DoesNotExist, ValueError):
                messages.error(request, "❌ Выбранный ПВЗ не существует.")
                return redirect("cargopart")

        user.full_name = full_name
        user.phone_number = phone_number
        user.pickup_point = pvz
        user.warehouse_address = warehouse_address
        user.id_user = generate_code_from_pvz(user)

        if password:
            if password == confirm_password:
                if len(password) < 6:
                    messages.error(request, "❌ Пароль должен содержать минимум 6 символов!")
                    return redirect("cargopart")
                print("✅ Пароль изменен!")
                user.set_password(password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "✅ Пароль успешно изменен!")
                logger.info("Пароль успешно обновлен!")
                return redirect("cargopart")
            else:
                messages.error(request, "❌ Пароли не совпадают!")
                logger.warning("Ошибка: пароли не совпадают!")
                return redirect("cargopart")

        user.save()
        messages.success(request, "✅ Данные успешно обновлены!")
        return redirect("cargopart")

    # settings = Settings.objects.first()

    user_data = {
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "pickup_point": user.pickup_point.id if user.pickup_point else None,
        "warehouse_address": user.warehouse_address or "",
        "pvz_list": Pvz.objects.all(),
        "id_user": user.id_user,
    }
    return render(request, "Cargopart.html", {
        "user_data": user_data,
        "user": user,
        # "settings": settings,
    })

def warehouse(request):
    # settings = Settings.objects.latest("id")
    query = request.GET.get('q') 
    products = Product.objects.all()

    if query:
        products = products.filter(track__icontains=query)  

    page_obj = paginate_queryset(products, request, per_page=15)

    return render(request, "warehouse.html", {
        "products": page_obj,  
        "query": query,
        # 'settings': settings,
        "products": page_obj,
        "query": query
    })

def scaner(request):
    context = {
        'ProductStatus': ProductStatus,
        'current_status': 'in_transit'
    }
    return render(request, "scaner.html", {'context': context})

# @login_required
def manager(request):
    track = request.GET.get('track', '')
    statuses = ProductStatus.choices
    return render(request, 'manager.html', {'track': track, 'statuses': statuses})


@csrf_exempt
def save_track(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Метод запроса должен быть POST"}, status=405)

    track = request.POST.get("track")
    weight = request.POST.get("weight")

    logger.debug(f"Получен запрос: track={track}, weight={weight}")

    if not track:
        return JsonResponse({"success": False, "error": "Трек-номер обязателен"}, status=400)

    try:
        product, created = Product.objects.get_or_create(
            track=track,
            defaults={"status": ProductStatus.IN_TRANSIT, 'created_by_manager': True}
        )

        if created:
            logger.debug(f"Новый товар {track} добавлен со статусом 'В пути'")
            return JsonResponse({
                "success": True,
                "message": f"✅ Новый товар {track} добавлен со статусом 'В пути'!",
                "status": product.status,
                "redirect": True
            })

        if product.status == ProductStatus.WAITING_FOR_ARRIVAL:
            product.status = ProductStatus.IN_TRANSIT
            product.save()
            logger.debug(f"Товар {track} обновлён до статуса 'В пути'")
            return JsonResponse({
                "success": True,
                "message": f"✅ Статус товара {track} обновлён до 'В пути'!",
                "status": product.status,
                "redirect": True
            })

        if product.status == ProductStatus.IN_TRANSIT:
            if not weight:
                logger.debug(f"Товар {track} в статусе 'В пути', требуется ввод веса")
                return JsonResponse({
                    "success": True,
                    "message": f"✍️ Товар {track} найден в статусе 'В пути'. Введите вес для продолжения.",
                    "status": product.status,
                    "require_weight": True
                })
            else:
                try:
                    product.weight = float(weight)
                except ValueError:
                    logger.error(f"Некорректный формат веса: {weight}")
                    return JsonResponse({"success": False, "error": "Некорректный формат веса"}, status=400)
                
                product.status = ProductStatus.IN_OFFICE
                product.save()
                logger.debug(f"Вес установлен, товар {track} обновлён до статуса 'В офисе'")

                # Отправка уведомления через Telegram с использованием безопасного запуска асинхронной задачи
                if product.user and product.user.chat_id:
                    message = f"📦 Ваш товар с трек-номером {track} прибыл в офис! Вес: {product.weight} кг. Заберите его в удобное время."
                    async_to_sync(send_telegram_message)(product.user.chat_id, message, track_number=track)
                    logger.debug(f"Уведомление отправлено пользователю {product.user.full_name} для трека {track}")



                return JsonResponse({
                    "success": True,
                    "message": f"✅ Товар {track} прибыл в офис! Пользователь уведомлён.",
                    "status": product.status,
                    "redirect": True
                })

        return JsonResponse({
            "success": True,
            "message": f"ℹ️ Товар {track} уже находится в статусе '{product.get_status_display()}'.",
            "status": product.status
        })

    except Exception as e:
        logger.error(f"Ошибка при обработке запроса: {e}")
        return JsonResponse({"success": False, "error": f"Ошибка: {e}"}, status=500)

@login_required
def mainpasels(request):
    # settings = Settings.objects.latest("id")
    """Главная страница с посылками пользователя"""
    user = request.user
    status_filter = request.GET.get('status', 'in_office')
    status_filter = request.GET.get('status', 'in_office')
    search_form = TrackingSearchForm(request.GET)
    if status_filter == 'delivered':
        parcels = Product.objects.filter(user=user, status="delivered").order_by('-created_at')
    else:
        parcels = Product.objects.filter(user=user, status="in_office").order_by('-created_at')
    if search_form.is_valid() and search_form.cleaned_data['track']:
        parcels = parcels.filter(track__icontains=search_form.cleaned_data['track'])
    total_weight = sum(parcel.weight for parcel in parcels)
    total_price = sum(parcel.price for parcel in parcels)

    return render(request, "mainpasels.html", {
        'parcels': parcels,
        'status_filter': status_filter,
        'search_form': search_form,
        'total_count': parcels.count(),
        'total_weight': round(total_weight, 2),
        'total_price': round(total_price, 2),
        # 'settings': settings,
        
    })


@method_decorator(login_required, name='dispatch')
class ParcelView(View):
    # settings = Settings.objects.latest("id")
    def get(self, request, action=None, track=None):
        if action == "search":
            return self.track_search(request)
        elif action == "my-parcels":
            return self.my_parcels(request)
        return redirect("mainpasels")

    def post(self, request, action=None, track=None):
        if action == "add":
            return self.add_tracking(request, track)
        return redirect("mainpasels")

    def track_search(self, request):
        track = request.GET.get("track", "").strip()
        searched_product = None

        if track:
            try:
                searched_product = Product.objects.get(track=track)
            except Product.DoesNotExist:
                messages.error(request, "Товар с таким трек-номером не найден.")
                return redirect("mainpasels")

        return render(request, "mainpasels.html", {
            "searched_product": searched_product,
        })

    def add_tracking(self, request, track):
        user = request.user
        try:
            product = Product.objects.get(track=track)

            if product.user:
                messages.error(request, "Этот товар уже принадлежит другому пользователю.")
            else:
                product.user = user
                product.save()
                messages.success(request, f"Товар {track} успешно добавлен в ваш аккаунт.")

        except Product.DoesNotExist:
            messages.error(request, "Товар с таким трек-номером не найден.")

        return redirect("mainpasels")

    def my_parcels(self, request):
        user_products = Product.objects.filter(user=request.user).order_by("-created_at")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            products_data = [
                {
                    "track": p.track,
                    "status": p.get_status_display(),
                    "weight": p.weight,
                    "price": p.price,
                }
                for p in user_products
            ]
            return JsonResponse({"user_products": products_data})

        return render(request, "mainpasels.html", {
            "user_products": user_products,
            "no_products": not user_products.exists(),
        })


def past(request):
    return render(request, "Past.html", locals())

def unknown(request):
    # settings = Settings.objects.latest("id")
    query = request.GET.get('q', '')
    if query:
        unknown_products = Product.objects.filter(status=ProductStatus.UNKNOWN, track__icontains=query)
    else:
        unknown_products = Product.objects.filter(status=ProductStatus.UNKNOWN)
    
    # return render(request, 'Unknown.html', {'unknown_products': unknown_products, 'query': query, 'settings': settings})
