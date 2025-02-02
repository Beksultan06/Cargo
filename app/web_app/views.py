import logging, json
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from app.web_app.models import User, Pvz, Product
from app.web_app.pagination import paginate_queryset
from .models import ProductStatus, User, Pvz, Product
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from app.web_app.forms import TrackingSearchForm
from django.utils.decorators import method_decorator
from django.views import View

logger = logging.getLogger(__name__)

def register(request):
    chat_id = request.GET.get('chat_id') or request.POST.get('chat_id')

    logging.info(f"Полученный chat_id в register: {chat_id}")

    if chat_id:
        user = User.objects.filter(chat_id=chat_id).first()
        if user:
            login(request, user)
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
                messages.success(request, '✅ Регистрация и авторизация прошли успешно!')
                return redirect('cargopart')

        except Exception as e:
            logging.error(f"Ошибка при регистрации: {e}")
            messages.error(request, f'❌ Ошибка при регистрации: {e}')
            return render(request, 'index.html', {'pvz_list': Pvz.objects.all()})

    return render(request, 'index.html', {'pvz_list': Pvz.objects.all()})


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
    user_data = {
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "pickup_point": user.pickup_point.id if user.pickup_point else None,
        "warehouse_address": user.warehouse_address or "",
        "pvz_list": Pvz.objects.all(),
    }
    return render(request, "Cargopart.html", locals())


def warehouse(request):
    query = request.GET.get('q') 
    products = Product.objects.all()

    if query:
        products = products.filter(track__icontains=query)  

    page_obj = paginate_queryset(products, request, per_page=1)  # Показываем 10 товаров на странице

    return render(request, "warehouse.html", {
        "products": page_obj,  
        "query": query
    })

def scaner(request):
    return render(request, "scaner.html", locals())

# @login_required
def manager(request):
    track = request.GET.get('track', '')
    statuses = ProductStatus.choices
    return render(request, 'manager.html', {'track': track, 'statuses': statuses})

@csrf_exempt
# @login_required
def save_track(request):
    if request.method == "POST":
        try:
            track = request.POST.get("track")
            status = request.POST.get("status")
            weight = request.POST.get("weight")
            if not track or not status or not weight:
                return JsonResponse({"success": False, "error": "Заполните все поля"}, status=400)
            weight = float(weight)
            product, created = Product.objects.get_or_create(track=track, defaults={"weight": weight, "status": status, "created_by_manager": True})
            if not created:
                product.weight = weight
                product.status = status
                product.created_by_manager = True
                product.save()
                return redirect("/scanner/")
            return JsonResponse({"success": True, "message": f"Товар {track} сохранён!"})
        except ValueError:
            return JsonResponse({"success": False, "error": "Некорректный формат веса"}, status=400)
    return JsonResponse({"success": False, "error": "Метод запроса должен быть POST"}, status=405)


@login_required
def mainpasels(request):
    """Главная страница с посылками пользователя"""
    user = request.user
    status_filter = request.GET.get('status', 'in_office')  # Фильтр по статусу
    search_form = TrackingSearchForm(request.GET)

    # Фильтруем посылки по статусу
    if status_filter == 'delivered':
        parcels = Product.objects.filter(user=user, status="delivered").order_by('-created_at')
    else:
        parcels = Product.objects.filter(user=user, status="in_office").order_by('-created_at')

    # Если введён трек-номер - ищем конкретную посылку
    if search_form.is_valid() and search_form.cleaned_data['track']:
        parcels = parcels.filter(track__icontains=search_form.cleaned_data['track'])

    # Подсчитываем статистику
    total_weight = sum(parcel.weight for parcel in parcels)
    total_price = sum(parcel.price for parcel in parcels)

    return render(request, "mainpasels.html", {
        'parcels': parcels,
        'status_filter': status_filter,
        'search_form': search_form,
        'total_count': parcels.count(),
        'total_weight': round(total_weight, 2),
        'total_price': round(total_price, 2),
    })


@method_decorator(login_required, name='dispatch')
class ParcelView(View):

    def get(self, request, action=None, track=None):
        """Обрабатывает GET-запросы для поиска и просмотра посылок"""
        if action == "search":
            return self.track_search(request)
        elif action == "my-parcels":
            return self.my_parcels(request)
        return redirect("mainpasels")

    def post(self, request, action=None, track=None):
        """Обрабатывает POST-запрос для добавления посылки"""
        if action == "add":
            return self.add_tracking(request, track)
        return redirect("mainpasels")

    def track_search(self, request):
        """Поиск товара по трек-номеру"""
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
        """Присвоить товар пользователю"""
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
        """Вывод всех посылок пользователя (Поддержка AJAX)"""
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