from django.urls import path
from app.web_app.views import index

urlpatterns = [
    path("", index, name='index')
]
