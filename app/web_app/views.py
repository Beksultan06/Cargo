from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from django.contrib import messages
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
            messages.error(request, 'Все поля обязательны для заполнения.')
            return render(request, 'index.html', {'pvz_list': Pvz.objects.all()})

        if password != confirm_password:
            messages.error(request, 'Пароли не совпадают.')
            return render(request, 'index.html', {'pvz_list': Pvz.objects.all()})

        try:
            pvz = Pvz.objects.get(id=pvz_id)
        except Pvz.DoesNotExist:
            messages.error(request, 'Выбранный ПВЗ не существует.')
            return render(request, 'index.html', {'pvz_list': Pvz.objects.all()})

        if User.objects.filter(phone_number=phone).exists():
            messages.error(request, 'Пользователь с таким номером телефона уже зарегистрирован.')
            return render(request, 'index.html', {'pvz_list': Pvz.objects.all()})

        try:
            new_user = User.objects.create(
                full_name=full_name,
                phone_number=phone,
                pickup_point=pvz,
                address=address,
                username=phone,  # добавляем username, если он уникален
                password=make_password(password),
            )
            messages.success(request, 'Регистрация прошла успешно.')
            return redirect('success')
        except Exception as e:
            messages.error(request, f'Ошибка при регистрации: {e}')
            return render(request, 'index.html', {'pvz_list': Pvz.objects.all()})

    return render(request, 'index.html', {'pvz_list': Pvz.objects.all()})

def success(request):
    return render(request, 'success.html')


def cargopart(request):
    return render(request, 'Cargopart.html')