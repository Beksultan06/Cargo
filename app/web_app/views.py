import logging, json, re
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from app.telegram.management.commands.app.bot import notify_registration_success, send_telegram_message
from app.web_app.models import User, Pvz, Product
from app.web_app.pagination import paginate_queryset
from .models import ProductStatus, Settings, User, Pvz, Product, generate_code_from_pvz
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from app.web_app.forms import TrackingSearchForm
from django.utils.decorators import method_decorator
from django.views import View
from django.middleware.csrf import get_token
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)

from django.core.exceptions import ObjectDoesNotExist
def register(request):
    try:
        settings_obj = Settings.objects.latest('id')
    except ObjectDoesNotExist:
        settings_obj = None
        logger.warning("Настройки не найдены. Проверьте таблицу Settings.")

    chat_id = request.GET.get('chat_id') or request.POST.get('chat_id')
    logger.info(f"Полученный chat_id в register: {chat_id}")

    if chat_id:
        user = User.objects.filter(chat_id=chat_id).first()
        if user:
            logger.info(f"Пользователь с chat_id {chat_id} уже зарегистрирован. Перенаправление в личный кабинет.")
            login(request, user)
            return redirect('cargopart')

    if request.method == 'POST':
        full_name = request.POST.get('fullName', '').strip()
        phone = request.POST.get('phone', '').strip()
        pvz_id = request.POST.get('pvz')
        address = request.POST.get('address', '').strip()
        password = request.POST.get('password', '').strip()
        confirm_password = request.POST.get('confirmPassword', '').strip()

        if not all([full_name, phone, pvz_id, address, password, confirm_password]):
            logger.warning("Не все поля заполнены.")
            return render(request, 'index.html', {
                'pvz_list': Pvz.objects.all(),
                'settings': settings_obj,
                'error_message': '❌ Все поля обязательны для заполнения.'
            })

        if password != confirm_password:
            logger.warning("Пароли не совпадают.")
            return render(request, 'index.html', {
                'pvz_list': Pvz.objects.all(),
                'settings': settings_obj,
                'error_message': '❌ Пароли не совпадают.'
            })

        try:
            pvz = Pvz.objects.get(id=pvz_id)
        except Pvz.DoesNotExist:
            logger.error(f"ПВЗ с id {pvz_id} не найден.")
            return render(request, 'index.html', {
                'pvz_list': Pvz.objects.all(),
                'settings': settings_obj,
                'error_message': '❌ Выбранный ПВЗ не существует.'
            })

        if User.objects.filter(phone_number=phone).exists():
            logger.warning(f"Пользователь с номером {phone} уже зарегистрирован.")
            return render(request, 'index.html', {
                'pvz_list': Pvz.objects.all(),
                'settings': settings_obj,
                'error_message': '❌ Пользователь с таким номером телефона уже зарегистрирован.'
            })

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
            logger.info(f"Создан новый пользователь {new_user.username} с chat_id: {new_user.chat_id}")

            user = authenticate(request, username=phone, password=password)
            if user:
                login(request, user)
                async_to_sync(notify_registration_success)(chat_id, full_name)
                return redirect('cargopart')

        except Exception as e:
            logger.error(f"Ошибка при регистрации: {e}")
            return render(request, 'index.html', {
                'pvz_list': Pvz.objects.all(),
                'settings': settings_obj,
                'error_message': f'❌ Ошибка при регистрации: {e}'
            })

    return render(request, 'index.html', {
        'pvz_list': Pvz.objects.all(),
        'settings': settings_obj
    })


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

def cargopart(request):
    # Попытка авто-входа через chat_id и auto_login
    chat_id = request.GET.get('chat_id')
    auto_login = request.GET.get('auto_login', 'false').lower() == 'true'
    
    logger.info(f"Полученный chat_id: {chat_id}, auto_login: {auto_login}")

    if chat_id and auto_login:
        user = User.objects.filter(chat_id=chat_id).first()
        if user:
            login(request, user)
            logger.info(f"Пользователь {user.full_name} автоматически вошел в систему.")
            return redirect('/cargopart/')  # Перенаправление на страницу после успешного входа
        else:
            logger.warning(f"Пользователь с chat_id {chat_id} не найден.")
            return redirect('/')  # Перенаправление на главную, если пользователь не найден

    # Если пользователь уже аутентифицирован
    if request.user.is_authenticated:
        user = request.user
    else:
        # Если нет параметров для авто-входа и пользователь не аутентифицирован
        return redirect('/')

    if request.method == "POST":
        # Обработка формы обновления данных
        full_name = request.POST.get("full_name", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        pvz_id = request.POST.get("pickup_point", "").strip()
        warehouse_address = request.POST.get("warehouse_address", "").strip()
        password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get("confirm-password", "").strip()

        # Проверка выбранного ПВЗ
        pvz = None
        if pvz_id:
            try:
                pvz = Pvz.objects.get(id=int(pvz_id))
            except (Pvz.DoesNotExist, ValueError):
                messages.error(request, "❌ Выбранный ПВЗ не существует.")
                return redirect("cargopart")

        # Обновление данных пользователя
        user.full_name = full_name
        user.phone_number = phone_number
        user.pickup_point = pvz
        user.warehouse_address = warehouse_address

        if password:
            if password == confirm_password:
                if len(password) < 6:
                    messages.error(request, "❌ Пароль должен содержать минимум 6 символов!")
                    return redirect("cargopart")
                user.set_password(password)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, "✅ Пароль успешно изменен!")
                return redirect("cargopart")
            else:
                messages.error(request, "❌ Пароли не совпадают!")
                return redirect("cargopart")

        user.save()
        messages.success(request, "✅ Данные успешно обновлены!")
        return redirect("cargopart")

    settings = Settings.objects.first()
    user_data = {
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "pickup_point": user.pickup_point.id if user.pickup_point else None,
        "warehouse_address": user.warehouse_address or "",
        "pvz_list": Pvz.objects.all(),
        "id_user": user.id_user,
        "settings":settings
    }
    
    return render(request, "Cargopart.html", {
        "user_data": user_data,
        "user": user,
        "settings": settings,
    })

def warehouse(request):
    settings = Settings.objects.latest("id")
    query = request.GET.get('q') 
    products = Product.objects.all()

    if query:
        products = products.filter(track__icontains=query)  

    page_obj = paginate_queryset(products, request, per_page=15)

    return render(request, "warehouse.html", {
        "products": page_obj,  
        "query": query,
        'settings': settings,
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

                # Отправка уведомления через функцию send_telegram_message
                if product.user and product.user.chat_id:
                    async_to_sync(send_telegram_message)(product.user.chat_id, product)

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



def mainpasels(request):
    settings = Settings.objects.latest("id")
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
        'settings': settings,
        
    })


# @method_decorator(name='dispatch')
class ParcelView(View):
    def dispatch(self, request, *args, **kwargs):
        self.settings = Settings.objects.latest("id")  # Загружаем настройки перед каждым запросом
        return super().dispatch(request, *args, **kwargs)

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
        log_message = None

        if track:
            try:
                searched_product = Product.objects.get(track=track)
            except Product.DoesNotExist:
                log_message = "Товар с таким трек-номером не найден."
                return self.render_with_settings(request, "mainpasels.html", {"log_message": log_message})

        return self.render_with_settings(request, "mainpasels.html", {
            "searched_product": searched_product,
            "log_message": log_message,
        })

    def add_tracking(self, request, track):
        user = request.user
        log_message = None

        try:
            product = Product.objects.get(track=track)
            if product.user:
                log_message = "Этот товар уже принадлежит другому пользователю."
            else:
                product.user = user
                product.save()
                log_message = f"Товар {track} успешно добавлен в ваш аккаунт."
        except Product.DoesNotExist:
            log_message = "Товар с таким трек-номером не найден."

        return self.render_with_settings(request, "mainpasels.html", {"log_message": log_message})

    def my_parcels(self, request):
        user_products = Product.objects.filter(user=request.user).order_by("-created_at")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            products_data = [
                {
                    "track": p.track,
                    "status": p.get_status_display(),
                    "weight": p.weight,
                    "price": p.price
                }
                for p in user_products
            ]
            return JsonResponse({"user_products": products_data})

        return self.render_with_settings(request, "mainpasels.html", {
            "user_products": user_products,
            "no_products": not user_products.exists(),
        })

    def render_with_settings(self, request, template_name, context):
        """Упрощённый рендер с добавлением settings в контекст"""
        context["settings"] = self.settings
        return render(request, template_name, context)


def past(request):
    return render(request, "Past.html", locals())

def unknown(request):
    settings = Settings.objects.latest("id")
    query = request.GET.get('q', '')
    if query:
        unknown_products = Product.objects.filter(status=ProductStatus.UNKNOWN, track__icontains=query)
    else:
        unknown_products = Product.objects.filter(status=ProductStatus.UNKNOWN)
    
    return render(request, 'Unknown.html', {'unknown_products': unknown_products, 'query': query, 'settings': settings})
