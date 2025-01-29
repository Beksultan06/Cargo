# Generated by Django 4.2 on 2025-01-29 10:34

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("web_app", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="phone_number",
            field=models.CharField(
                max_length=20, unique=True, verbose_name="Номер телефона"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="warehouse_address",
            field=models.TextField(blank=True, null=True, verbose_name="Адрес склада"),
        ),
    ]
