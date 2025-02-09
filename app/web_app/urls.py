from django.urls import path
from app.web_app.views import register, cargopart, warehouse, mainpasels, scaner, save_track, manager,\
login_view, ParcelView, unknown

urlpatterns = [
    path("", register, name='register'),
    path("cargopart/", cargopart, name='cargopart'),
    path("warehouse/", warehouse, name='warehouse'),
    path("mainpasels/", mainpasels, name='mainpasels'),
    path("track-search/", ParcelView.as_view(), name="track_search"),
    path("track-search/<str:action>/", ParcelView.as_view(), name="track_search_action"),
    path("track-search/<str:action>/<str:track>/", ParcelView.as_view(), name="track_search_track"),
    path("scanner/", scaner, name='scanner'),
    path("manager/", manager, name='manager'),
    path("save_track/", save_track, name='save_track'),
    path("login/", login_view, name='login'),
    path("unknown/", unknown, name='unknown')
]