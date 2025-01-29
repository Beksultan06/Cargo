import logging, json
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .models import User, Pvz, Product
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

def register(request):
    chat_id = request.GET.get('chat_id') or request.POST.get('chat_id')

    logging.info(f"Полученный chat_id в register: {chat_id}")

    if chat_id:
        user = User.objects.filter(chat_id=chat_id).first()
        if user:
            login(request, user)  # ✅ Автоматически логиним пользователя
            return redirect('cargopart')  # ✅ Перенаправляем на личный кабинет

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
    """Страница личного кабинета (Cargopart), доступна только авторизованным пользователям"""
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
    return render(request, "warehouse.html")

def mainpasels(request):
    return render(request, 'mainpasels.html', locals())

def scaner(request):
    return render(request, "scaner.html", locals())

@login_required
def manager(request):
    """Страница менеджера с авто-заполнением трек-номера"""
    track = request.GET.get('track', '')  
    return render(request, 'manager.html', {'track': track})

@login_required
def save_track(request):
    """Сохраняет трек-номер в базу данных"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            track = data.get("track")

            if not track:
                return JsonResponse({"success": False, "error": "Трек-номер отсутствует"}, status=400)

            # Создаём новый продукт с трек-номером
            product, created = Product.objects.get_or_create(track=track, defaults={"weight": 0})

            return JsonResponse({"success": True, "message": f"Трек-номер {track} сохранён!"})
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Ошибка обработки данных"}, status=400)

    return JsonResponse({"success": False, "error": "Метод запроса должен быть POST"}, status=405)