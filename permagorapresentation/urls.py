# cal/urls.py

from . import views
from django.urls import path, include

app_name = 'permagorapresentation'

urlpatterns = [
    path('', views.accueil, name="accueil"),
]
