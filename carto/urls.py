# cal/urls.py

from django.urls import path, include, re_path
from . import views

app_name = 'carto'
urlpatterns = [
    re_path(r'', views.carte, name='carte'),
]
