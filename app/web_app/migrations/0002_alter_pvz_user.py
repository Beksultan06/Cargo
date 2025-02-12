# Generated by Django 4.2 on 2025-02-12 08:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('web_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pvz',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pvz', to=settings.AUTH_USER_MODEL, verbose_name='Пользователь'),
        ),
    ]
