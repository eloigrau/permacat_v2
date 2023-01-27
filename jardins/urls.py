# -*- coding: utf-8 -*-
"""bourseLibre URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog__ import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog__/', include(blog_urls))
"""
from django.conf.urls import url
from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'jardins'

urlpatterns = [
    url(r'^accueil/$', views.accueil, name="accueil"),
    url(r'^import_db_inpn_0/$', views.import_db_inpn_0, name="import_db_inpn_0"),
    url(r'^import_db_inpn_1/$', views.import_db_inpn_1, name="import_db_inpn_1"),
    url(r'^import_db_inpn_2/$', views.import_db_inpn_2, name="import_db_inpn_2"),
    url(r'^import_db_inpn_3/$', views.import_db_inpn_3, name="import_db_inpn_3"),
    url(r'^import_db_inpn_4/$', views.import_db_inpn_4, name="import_db_inpn_4"),
    path(r'plantes/', login_required(views.ListePlantes.as_view(), login_url='/auth/login/'), name="plantes"),
    path(r'voir_plante/<str:cd_nom>', views.voir_plante, name="voir_plante"),
    path(r'voir_plante_nom/', views.voir_plante_nom, name="voir_plante_nom"),
    path(r'voir_plante_recherche/', views.voir_plante_recherche, name="voir_plante_recherche"),
    url(r'^plante-ac/$', login_required(views.PlanteAutocomplete.as_view(), login_url='/auth/login/'), name='plante-ac',),
    url(r'^ajouterPlante/$', views.ajouter_plante, name="ajouter_plante"),
]
