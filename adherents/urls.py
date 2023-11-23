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

app_name = 'adherents'

urlpatterns = [
    url(r'^$', views.ListeAdherents.as_view(), name="accueil"),
    url(r'^accueil_admin/$', views.accueil_admin, name="accueil_admin"),

    url(r'^import_csv/$', views.import_adherents_ggl, name="import_csv"),

    path(r'adherents/', login_required(views.ListeAdherents.as_view()), name="adherent_liste"),
    path(r'adherent/ajouter/', views.adherent_ajouter, name="adherent_ajouter"),
    path(r'adherent/detail/<int:pk>', login_required(views.AdherentDetailView.as_view()), name="adherent_detail"),
    path(r'adherent/modifier/<int:pk>', login_required(views.AdherentUpdateView.as_view()), name="adherent_modifier"),
    path(r'adherent/adherents_modifier_adresse/<int:pk>', login_required(views.AdherentAdresseUpdateView.as_view()), name="adherents_modifier_adresse"),
    path(r'adherent/supprimer/<int:pk>', login_required(views.AdherentDeleteView.as_view()), name="adherent_supprimer"),

    path(r'adhesions/', login_required(views.ListeAdhesions.as_view()), name="adhesion_liste"),
    path(r'adhesion/creer/<int:adherent_pk>', views.ajouterAdhesion, name="adhesion_creer"),
    path(r'adhesion/detail/<int:pk>', login_required(views.AdhesionDetailView.as_view()), name="adhesion_detail"),
    path(r'adhesion/modifier/<int:pk>', login_required(views.AdhesionUpdateView.as_view()), name="adhesion_modifier"),
    path(r'adhesion/supprimer/<int:pk>', login_required(views.AdhesionDeleteView.as_view()), name="adhesion_supprimer"),

     ]
