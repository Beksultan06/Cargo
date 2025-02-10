# Generated by Django 4.2 on 2025-02-09 15:58

import ckeditor.fields
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('chat_id', models.BigIntegerField(blank=True, null=True, verbose_name='Chat ID')),
                ('id_user', models.CharField(blank=True, max_length=10, null=True, unique=True, verbose_name='Айди')),
                ('code', models.CharField(blank=True, max_length=10, null=True, unique=True, verbose_name='Код')),
                ('full_name', models.CharField(max_length=255, verbose_name='ФИО')),
                ('phone_number', models.CharField(max_length=20, unique=True, verbose_name='Номер телефона')),
                ('address', models.TextField(verbose_name='Адрес')),
                ('warehouse_address', models.TextField(blank=True, null=True, verbose_name='Адрес склада')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
            ],
            options={
                'verbose_name': 'Пользователь',
                'verbose_name_plural': 'Пользователи',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Manager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=155, verbose_name='Имя пользователя')),
                ('full_name', models.CharField(max_length=150, verbose_name='ФИО')),
                ('password', models.CharField(max_length=10, verbose_name='пароль')),
            ],
            options={
                'verbose_name': 'Менеджер',
                'verbose_name_plural': 'Менеджеры',
            },
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', ckeditor.fields.RichTextField(verbose_name='Текст')),
            ],
            options={
                'verbose_name_plural': 'Уведомление',
            },
        ),
        migrations.CreateModel(
            name='Settings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.ImageField(upload_to='image/', verbose_name='Логотип')),
                ('address', models.CharField(max_length=100, verbose_name='Адрес')),
                ('phone', models.CharField(help_text='Тут нужен рабочий номер склада в Китае', max_length=50, verbose_name='Номер телефона')),
                ('price', models.FloatField(verbose_name='Цена за кг')),
                ('ista', models.URLField(blank=True, null=True, verbose_name='Инстаграмм')),
                ('watapp', models.URLField(blank=True, null=True, verbose_name='Ватсап')),
                ('about', ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='О нас')),
                ('instructions', ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='инструкция')),
                ('prohibited_goods', ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='запрещенные товары')),
                ('address_tg_bot', ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Адрес склада')),
                ('support', ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Поддержка')),
            ],
            options={
                'verbose_name': 'Основная настройка',
                'verbose_name_plural': 'Основные настройки',
            },
        ),
        migrations.CreateModel(
            name='Pvz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.CharField(blank=True, max_length=100, null=True, verbose_name='ПВЗ')),
                ('slug', models.TextField(null=True, unique=True, verbose_name='SLUG')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pvz', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'ПВЗ',
                'verbose_name_plural': 'ПВЗ',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('track', models.CharField(max_length=70, verbose_name='Трек номер')),
                ('weight', models.FloatField(blank=True, help_text='Килограм товара', null=True, verbose_name='КГ')),
                ('price', models.FloatField(editable=False, help_text='Автоматически рассчитывается', verbose_name='Цена ($)')),
                ('status', models.CharField(choices=[('waiting', 'Ожидает поступления'), ('in_transit', 'В пути'), ('in_office', 'В офисе'), ('courier_in_transit', 'Курьер в пути'), ('delivered', 'Доставлен'), ('unknown', 'Неизвестный товар')], default='waiting', max_length=20, verbose_name='Статус')),
                ('created_by_manager', models.BooleanField(default=False, verbose_name='Добавлено менеджером')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата создания')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Товар',
                'verbose_name_plural': 'Товары',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Courier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(help_text='Введите адрес доставки', max_length=155, verbose_name='Адрес')),
                ('phone', models.CharField(help_text='Введите номер телефона', max_length=20, verbose_name='Номер телефона')),
                ('type_payment', models.CharField(choices=[('MBANK', 'MBANK'), ('Наличный', 'Наличный')], max_length=20, verbose_name='Тип платежа')),
                ('status', models.CharField(editable=False, max_length=20, verbose_name='Статус доставки')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('track', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='web_app.product', verbose_name='Трек номер')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Пользователь')),
            ],
            options={
                'verbose_name': 'Курьер',
                'verbose_name_plural': 'Курьеры',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddField(
            model_name='user',
            name='pickup_point',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users', to='web_app.pvz', verbose_name='ПВЗ'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions'),
        ),
    ]
