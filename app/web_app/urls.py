from django.urls import path
from app.web_app.views import register, cargopart, warehouse

urlpatterns = [
    path("", register, name='register'),
    path("cargopart/", cargopart, name='cargopart'),
    path("warehouse/", warehouse, name='warehouse')
]