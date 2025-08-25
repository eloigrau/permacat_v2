# cal/urls.py

from . import views
from django.urls import path, include

app_name = 'ducepaujus'

urlpatterns = [
    path('', views.accueil, name="accueil_ducepaujus"),
]
