from django.apps import AppConfig


class WebAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.web_app"
    verbose_name="LiderCargo"

    def ready(self):
        import app.web_app.signals  # Убедитесь, что путь корректный