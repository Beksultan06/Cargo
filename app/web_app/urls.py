from django.urls import path
from app.web_app.views import register, cargopart, warehouse, mainpasels, scaner, save_track, manager

urlpatterns = [
    path("", register, name='register'),
    path("cargopart/", cargopart, name='cargopart'),
    path("warehouse/", warehouse, name='warehouse'),
    path("mainpasels/", mainpasels, name='mainpasels'),
    path("scanner/", scaner, name='scanner'),
    path("manager/", manager, name='manager'),
    path("save_track/", save_track, name='save_track'),
]