import logging
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from .models import User, Pvz

def register(request):
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
            # ✅ Создание пользователя
            new_user = User.objects.create(
                full_name=full_name,
                phone_number=phone,
                pickup_point=pvz,
                address=address,
                username=phone,
                password=make_password(password),  # Хэшируем пароль
            )

            # ✅ Автоматическая авторизация пользователя после регистрации
            user = authenticate(request, username=phone, password=password)
            if user:
                login(request, user)  # Логиним пользователя
                messages.success(request, '✅ Регистрация и авторизация прошли успешно!')

                # 🔄 Перенаправляем сразу в cargopart
                return redirect('cargopart')

        except Exception as e:
            messages.error(request, f'❌ Ошибка при регистрации: {e}')
            return render(request, 'index.html', {'pvz_list': Pvz.objects.all()})

    return render(request, 'index.html', {'pvz_list': Pvz.objects.all()})

logger = logging.getLogger(__name__)

@login_required(login_url='/')
def cargopart(request):
    """Страница личного кабинета (Cargopart), доступна только авторизованным пользователям"""
    
    user = request.user  

    if request.method == "POST":
        print("📩 Форма отправлена!")  # Проверяем, пришел ли POST-запрос
        print("📨 request.POST:", request.POST)  # Выводим все данные запроса

        full_name = request.POST.get("full_name", "").strip()
        phone_number = request.POST.get("phone_number", "").strip()
        pvz_id = request.POST.get("pickup_point", "").strip()
        warehouse_address = request.POST.get("warehouse_address", "").strip()
        password = request.POST.get("password", "").strip()
        confirm_password = request.POST.get("confirm-password", "").strip()

        logger.info(f"POST data: password={password}, confirm_password={confirm_password}")

        # Проверяем, существует ли ПВЗ с указанным ID
        pvz = None
        if pvz_id:
            try:
                pvz = Pvz.objects.get(id=int(pvz_id))  
            except (Pvz.DoesNotExist, ValueError):
                messages.error(request, "❌ Выбранный ПВЗ не существует.")
                return redirect("cargopart")

        # Обновляем данные пользователя
        user.full_name = full_name
        user.phone_number = phone_number
        user.pickup_point = pvz
        user.warehouse_address = warehouse_address

        # Проверяем, ввел ли пользователь новый пароль
        if password:
            if password == confirm_password:
                if len(password) < 6:
                    messages.error(request, "❌ Пароль должен содержать минимум 6 символов!")
                    return redirect("cargopart")

                print("✅ Пароль изменен!")  # Проверяем, выполняется ли смена пароля
                user.set_password(password)  # Устанавливаем новый пароль
                user.save()
                update_session_auth_hash(request, user)  # Чтобы не разлогинивало
                
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

    # Подготовка данных для шаблона
    user_data = {
        "full_name": user.full_name,
        "phone_number": user.phone_number,
        "pickup_point": user.pickup_point.id if user.pickup_point else None,  
        "warehouse_address": user.warehouse_address or "",
        "pvz_list": Pvz.objects.all(),
    }
    return render(request, "Cargopart.html", {"user_data": user_data})