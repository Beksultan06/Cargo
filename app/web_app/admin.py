from django.contrib import admin
from app.web_app.models import User, Pvz, Settings, Product
from django.utils.html import format_html


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
    
@admin.register(Settings)
class SettingsAdmin(admin.ModelAdmin):
    
    def logo_tag(self, obj):
        return format_html('<img src="{}" width="auto" height="50px" />'.format(obj.logo.url))

    logo_tag.short_description = 'Логотип'

    list_display = ('phone', 'address', 'logo_tag')
    
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('track weight price status created_at'.split())
    # readonly_fields = ('track', 'price')
    search_fields = ('track', 'status')
    list_editable = ('status',)
    