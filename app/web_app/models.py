from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
import random, string

def generate_user_id():
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    digits = ''.join(random.choices(string.digits, k=3))
    return letters + digits

def generate_code():
    return ''.join(random.choices(string.digits, k=10))

class Pvz(models.Model):
    city = models.CharField(verbose_name="ПВЗ", max_length=100, null=True, blank=True)
    user = models.ForeignKey(
        'User',  # Ссылаемся на модель пользователя
        on_delete=models.CASCADE, 
        related_name='pvz', 
        null=True, 
        blank=True, 
        verbose_name="Пользователь"
    )

    def __str__(self):
        return self.city

    class Meta:
        verbose_name = "ПВЗ"
        verbose_name_plural = "ПВЗ"


class User(AbstractUser):
    chat_id = models.BigIntegerField(null=True, blank=True, verbose_name="Chat ID")
    id_user = models.CharField(
        max_length=6,
        unique=True,
        default=generate_user_id,
        editable=False,
        verbose_name='Айди'
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        default=generate_code,
        editable=False
    )
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    phone_number = models.CharField(max_length=20, unique=True, verbose_name="Номер телефона")
    pickup_point = models.ForeignKey(
        Pvz,
        on_delete=models.CASCADE,
        verbose_name="ПВЗ",
        null=True,
        blank=True,
        related_name='users'
    )
    address = models.TextField(verbose_name="Адрес")
    warehouse_address = models.TextField(verbose_name="Адрес склада", blank=True, null=True)

    def __str__(self):
        return f"{self.full_name} ({self.id_user})"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

class Manager(models.Model):
    username = models.CharField(max_length=155, verbose_name='Имя пользователя')
    full_name = models.CharField(verbose_name="ФИО", max_length=150)
    password = models.CharField(max_length=10, verbose_name='пароль')

    def save(self, *args, **kwargs):
        if not self.pk or 'password' in self.get_dirty_fields():
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Менеджер"
        verbose_name_plural = "Менеджеры"