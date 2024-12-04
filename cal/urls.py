# cal/urls.py

from django.urls import path, include, re_path
from . import views

app_name = 'cal'
urlpatterns = [
    re_path(r'', views.agenda, name='agenda'),
]
