from django.db import models
from django.contrib.auth.models import AbstractUser
from ckeditor.fields import RichTextField
from django.contrib.auth.hashers import make_password, check_password
import random, string
from threading import Timer
from django.db.models.signals import pre_save
from django.dispatch import receiver
from slugify import slugify
import uuid

def generate_code_from_pvz(instance):
    if instance.pickup_point and instance.pickup_point.slug:
        slug_prefix = instance.pickup_point.slug[:3].upper()
        random_digits = ''.join(random.choices(string.digits, k=6))
        return f"{slug_prefix}-{random_digits}"
    return None

def generate_code():
    return ''.join(random.choices(string.digits, k=10))

class Pvz(models.Model):
    city = models.CharField(verbose_name="ПВЗ", max_length=100, null=True, blank=True)
    slug = models.TextField(
        verbose_name="SLUG",
        unique=True, null=True
    )
    user = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL, 
        related_name='pvz', 
        null=True, 
        blank=True, 
        verbose_name="Пользователь"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.city)
            self.slug = base_slug
            while Pvz.objects.filter(slug=self.slug).exists():
                unique_suffix = uuid.uuid4().hex[:6]
                self.slug = f"{base_slug}-{unique_suffix}"
        super().save(*args, **kwargs)


    def __str__(self):
        return self.city

    class Meta:
        verbose_name = "ПВЗ"
        verbose_name_plural = "ПВЗ"


class User(AbstractUser):
    chat_id = models.BigIntegerField(null=True, blank=True, verbose_name="Chat ID")
    id_user = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Айди'
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Код"
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

    REQUIRED_FIELDS = []

    def save(self, *args, **kwargs):
        if self.pickup_point:
            new_code = generate_code_from_pvz(self)
            if not self.code:
                self.code = new_code
            if not self.id_user:
                self.id_user = new_code

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.id_user})"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


@receiver(pre_save, sender=User)
def update_code_on_pvz_change(sender, instance, **kwargs):
    if instance.pickup_point:
        new_code = generate_code_from_pvz(instance)
        instance.code = new_code
        instance.id_user = new_code

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

def mbank_upload_path(instance, filename):
    return 'mbank/mbank.webp'

class Settings(models.Model):
    logo = models.ImageField(upload_to='image/', verbose_name="Логотип")
    address = models.CharField(max_length=100, verbose_name="Адрес склада в китае")
    phone = models.CharField(max_length=50, verbose_name="Номер телефона склада в Китае", help_text="Тут нужен рабочий номер склада в Китае")
    price = models.FloatField(verbose_name='Цена за кг')
    ista = models.URLField(verbose_name='Инстаграмм', blank=True, null=True)
    watapp = models.URLField(verbose_name='Ватсап', blank=True, null=True)
    about = RichTextField(verbose_name='О нас', blank=True, null=True)
    instructions = RichTextField(verbose_name='инструкция', blank=True, null=True)
    prohibited_goods = RichTextField(verbose_name='запрещенные товары', blank=True, null=True)
    address_tg_bot = RichTextField(verbose_name='Адрес склада', blank=True, null=True)
    support = RichTextField(verbose_name='Поддержка', blank=True, null=True)
    mbank = models.ImageField(upload_to=mbank_upload_path, verbose_name="Фото QR-кода от MBANK", blank=True, null=True)
    date = models.CharField(max_length=155, verbose_name='Часы работы')

    def __str__(self):
        return str(self.logo)

    class Meta:
        verbose_name = "Основная настройка"
        verbose_name_plural = "Основные настройки"

class ProductStatus(models.TextChoices):
    WAITING_FOR_ARRIVAL = "waiting", "Ожидает поступления"
    IN_TRANSIT = "in_transit", "В пути"
    IN_OFFICE = "in_office", "В офисе"
    COURIER_IN_TRANSIT = "courier_in_transit", "Курьер в пути"
    DELIVERED = "delivered", "Доставлен"
    COMPLETED = "completed", "Завершён"
    UNKNOWN = "unknown", "Неизвестный товар"

class Product(models.Model):
    user = models.ForeignKey('User', on_delete=models.SET_NULL, verbose_name='Пользователь', null=True, blank=True)
    track = models.CharField(max_length=70, verbose_name="Трек номер")
    weight = models.FloatField(verbose_name="КГ", help_text="Килограм товара", blank=True, null=True)
    price = models.FloatField(verbose_name="Цена ($)", help_text="Автоматически рассчитывается", editable=False)
    status = models.CharField(
        max_length=20,
        choices=ProductStatus.choices,
        default=ProductStatus.WAITING_FOR_ARRIVAL,
        verbose_name="Статус"
    )
    created_by_manager = models.BooleanField(default=False, verbose_name="Добавлено менеджером")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания", null=True)

    def save(self, *args, **kwargs):
        settings = Settings.objects.first()
        price_per_kg = settings.price if settings else 0
        self.price = round(self.weight * price_per_kg, 2) if self.weight else 0

        if not self.pk:
            if self.created_by_manager:
                self.status = ProductStatus.IN_TRANSIT
            else:
                existing_product = Product.objects.filter(track=self.track).exists()
                if not existing_product:
                    self.status = ProductStatus.WAITING_FOR_ARRIVAL

        super().save(*args, **kwargs)

    def update_status(self):
        if self.status == ProductStatus.WAITING_FOR_ARRIVAL and self.track:
            self.status = ProductStatus.IN_TRANSIT
        elif self.status == ProductStatus.IN_TRANSIT:
            self.status = ProductStatus.IN_OFFICE
        elif self.status == ProductStatus.IN_OFFICE:
            self.status = ProductStatus.COURIER_IN_TRANSIT
            self.save()
            Timer(2 * 60 * 60, self.set_delivered).start()
        elif self.status == ProductStatus.COURIER_IN_TRANSIT:
            self.status = ProductStatus.DELIVERED
        elif not self.track:
            self.status = ProductStatus.UNKNOWN
        self.save()

    def set_delivered(self):
        if self.status == ProductStatus.COURIER_IN_TRANSIT:
            self.status = ProductStatus.DELIVERED
            self.save()

    def __str__(self):
        return f"{self.track} - {self.get_status_display()} - {self.price}$"

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']


PAYMENT_CHOICES = (
    ("MBANK", "MBANK"),
    ("Наличный", "Наличный"),
)

class Courier(models.Model):
    user = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        verbose_name='Пользователь',
        null=True,
        blank=True
    )
    track = models.ForeignKey(
        'Product',
        on_delete=models.SET_NULL,
        verbose_name='Трек номер',
        null=True,
        blank=True
    )
    address = models.CharField(
        max_length=155,
        verbose_name='Адрес',
        help_text="Введите адрес доставки"
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Номер телефона',
        help_text="Введите номер телефона"
    )
    type_payment = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        verbose_name='Тип платежа'
    )
    status = models.CharField(
        max_length=20,
        verbose_name="Статус доставки",
        editable=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def save(self, *args, **kwargs):
        if self.track:
            self.status = self.track.status
        else:
            self.status = "Неизвестен"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Курьер для {self.track.track if self.track else 'Неизвестный трек'} - Статус: {self.status}"

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']
        
        
        
class CourierUser(models.Model):
    chat_id = models.CharField(max_length=20, unique=True, verbose_name="CHAT-ID")
    full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="ФИО")
    username = models.CharField(max_length=255, blank=True, null=True,)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"{self.full_name or self.username or self.chat_id}"
    
    class Meta:
        verbose_name = "Курьер"
        verbose_name_plural = "Курьеры"