from django.contrib import admin
from .models import User, Pvz

class PvzInline(admin.TabularInline):
    model = Pvz
    extra = 1
    verbose_name = "Пункт выдачи"
    verbose_name_plural = "Пункты выдачи"

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'id_user', 'phone_number', 'pickup_point', 'chat_id')
    search_fields = ('full_name', 'id_user', 'phone_number')
    list_filter = ('pickup_point',)
    # inlines = [PvzInline]

@admin.register(Pvz)
class PvzAdmin(admin.ModelAdmin):
    list_display = ('city',)
    search_fields = ('city',)