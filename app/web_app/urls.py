from django.urls import path
from app.web_app.views import register, success, cargopart

urlpatterns = [
    path("", register, name='register'),
    path("success/", success, name='success'),  # Исправил путь
    path("cargopart/", cargopart, name='cargopart')
]
