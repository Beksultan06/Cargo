from django.contrib import admin
from .models import User, Pvz

class PvzInline(admin.TabularInline):  # Используем TabularInline для отображения в табличном формате
    model = Pvz
    extra = 1  # Количество пустых строк для добавления новых записей
    verbose_name = "Пункт выдачи"
    verbose_name_plural = "Пункты выдачи"

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'id_user', 'phone_number', 'pickup_point', 'chat_id')  # Поля для отображения в списке
    search_fields = ('full_name', 'id_user', 'phone_number')  # Поля для поиска
    list_filter = ('pickup_point',)  # Фильтрация по полю ПВЗ
    inlines = [PvzInline]  # Добавляем Inline для ПВЗ

@admin.register(Pvz)
class PvzAdmin(admin.ModelAdmin):
    list_display = ('city',)  # Отображение поля "city" в списке
    search_fields = ('city',)  # Поля для поиска