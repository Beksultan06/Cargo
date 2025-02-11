from django.contrib import admin
from app.web_app.models import Notification, User, Pvz, Settings, Product, Manager, Courier, CourierUser
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.db.models import Sum
from datetime import datetime, timedelta
from openpyxl import Workbook
from django.http import HttpResponse
from django.db.models.functions import TruncMonth
from django.utils import timezone

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

@admin.register(CourierUser)
class CourierUserAdmin(admin.ModelAdmin):
    list_display = [
        'chat_id', 'full_name', 'username'
    ]
    list_filter = [
        'chat_id', 'full_name', 'username'
    ]
    search_fields = [
        'chat_id', 'full_name', 'username'
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('track', 'weight', 'price', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('track', 'status')
    list_editable = ('status',)
    change_list_template = "admin/product_change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('monthly-report/', self.admin_site.admin_view(self.monthly_report), name='monthly-report'),
            path('monthly-report/<int:year>/<int:month>/', self.admin_site.admin_view(self.month_detail), name='month-detail'),
            path('export-monthly-report/', self.admin_site.admin_view(self.export_monthly_report), name='export-monthly-report'),
            path('export-month-report/<int:year>/<int:month>/', self.admin_site.admin_view(self.export_month_report), name='export-month-report'),
        ]
        return custom_urls + urls

    # Месячный отчет
    def monthly_report(self, request):
        products = Product.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('price')).order_by('-month')
        context = {'monthly_data': products}
        return render(request, 'admin/monthly_report.html', context)

    # Отчет за месяц
    def month_detail(self, request, year, month):
        first_day = datetime(year, month, 1)
        last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        weeks = [
            (first_day + timedelta(days=i * 7), min(first_day + timedelta(days=(i + 1) * 7 - 1), last_day))
            for i in range(4)
        ]

        report_data = []
        total_sum = 0

        for i, (start_date, end_date) in enumerate(weeks, start=1):
            # Считаем сумму за неделю
            weekly_sum = Product.objects.filter(
                created_at__date__range=(start_date.date(), end_date.date())
            ).aggregate(total=Sum('price'))['total'] or 0

            # Собираем данные по каждому дню в неделе
            days_data = []
            current_date = start_date
            while current_date <= end_date:
                daily_sum = Product.objects.filter(
                    created_at__date=current_date.date()
                ).aggregate(total=Sum('price'))['total'] or 0

                days_data.append({
                    'day': current_date.day,
                    'date': current_date,
                    'daily_sum': daily_sum,
                })
                current_date += timedelta(days=1)

            report_data.append({
                'week': f'{i} неделя',
                'amount': weekly_sum,
                'start_date': start_date,
                'end_date': end_date,
                'days': days_data,
            })

            total_sum += weekly_sum

        context = {
            'report_data': report_data,
            'total_sum': total_sum,
            'year': year,
            'month': month,
        }

        return render(request, 'admin/month_detail.html', context)

    # Экспорт месячного отчета
    def export_monthly_report(self, request):
        products = Product.objects.annotate(month=TruncMonth('created_at')).values('month').annotate(total=Sum('price')).order_by('-month')
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = 'Месячный Отчет'

        sheet.append(['Месяц', 'Сумма'])
        for item in products:
            sheet.append([item['month'].strftime('%B %Y'), item['total']])

        return self._create_excel_response(workbook, 'monthly_report.xlsx')

    # Экспорт отчета за месяц
    def export_month_report(self, request, year, month):
        first_day = datetime(year, month, 1)
        last_day = (first_day + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        weeks = [(first_day + timedelta(days=i*7), min(first_day + timedelta(days=(i+1)*7 - 1), last_day)) for i in range(4)]

        workbook = Workbook()
        sheet = workbook.active
        sheet_title = f'Отчет {month}-{year}'
        sheet.title = sheet_title[:31]

        sheet.append(['Неделя', 'Сумма', 'Начало', 'Конец'])
        for i, (start_date, end_date) in enumerate(weeks, start=1):
            weekly_sum = Product.objects.filter(created_at__range=(start_date, end_date)).aggregate(total=Sum('price'))['total'] or 0
            sheet.append([f'{i} неделя', weekly_sum, start_date.strftime('%d-%m-%Y'), end_date.strftime('%d-%m-%Y')])

        return self._create_excel_response(workbook, f'month_report_{year}_{month}.xlsx')

    # Вспомогательный метод для создания Excel-ответа
    def _create_excel_response(self, workbook, filename):
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        workbook.save(response)
        return response