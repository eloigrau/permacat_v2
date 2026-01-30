# cal/urls.py

from . import views
from django.urls import path, include

app_name = 'collectifssa'

urlpatterns = [
    path('', views.accueil, name="accueil_collectifssa"),
]
