from django.contrib import admin
from app.web_app.models import Notification, User, Pvz, Settings, Product, Manager, Courier, CourierUser
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
    list_display = ('slug',)
    search_fields = ('slug',)
    prepopulated_fields = {'slug': ('city',)}


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
    list_filter = ('status',)
    search_fields = ('track', 'status')
    list_editable = ('status',)

@admin.register(Manager)
class ManagerAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'full_name']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['short_text']

    def short_text(self, obj):
        return (obj.text[:30] + '...') if len(obj.text) > 30 else obj.text

    short_text.short_description = 'Текст'
    
@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'track', 'status']
    list_filter = ['id', 'user', 'track', 'status']
    search_fields = ['user', 'track', 'status']
    
admin.site.register(CourierUser)