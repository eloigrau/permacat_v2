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
    url(r'^conf66/$', login_required(views.ListeAdherents.as_view()), name="accueil"),
    url(r'^conf66/accueil_admin/$', views.accueil_admin, name="accueil_admin"),
    url(r'^conf66/get_csv_adherents/$', views.get_csv_adherents, name="get_csv_adherents"),
    path(r'conf66/infos_adherents/<str:type_info>$', views.get_infos_adherent, name="get_infos_adherent"),

    url(r'^conf66/import_csv/$', views.import_adherents_ggl, name="import_csv"),
    url(r'^conf66/modif_APE/$', views.modif_APE, name="modif_APE"),

    path(r'conf66/adherents/', login_required(views.ListeAdherents.as_view()), name="adherent_liste"),
    path(r'conf66/adherent/ajouter/', views.adherent_ajouter, name="adherent_ajouter"),
    path(r'conf66/adherent/detail/<int:pk>', login_required(views.AdherentDetailView.as_view()), name="adherent_detail"),
    path(r'conf66/adherent/modifier/<int:pk>', login_required(views.AdherentUpdateView.as_view()), name="adherent_modifier"),
    path(r'conf66/adherent/adherents_modifier_adresse/<int:pk>', login_required(views.AdherentAdresseUpdateView.as_view()), name="adherents_modifier_adresse"),
    path(r'conf66/adherent/supprimer/<int:pk>', login_required(views.AdherentDeleteView.as_view()), name="adherent_supprimer"),

    path(r'conf66/adhesions/', login_required(views.ListeAdhesions.as_view()), name="adhesion_liste"),
    path(r'conf66/adhesion/creer/<int:adherent_pk>', views.ajouterAdhesion, name="adhesion_creer"),
    path(r'conf66/adhesion/detail/<int:pk>', login_required(views.AdhesionDetailView.as_view()), name="adhesion_detail"),
    path(r'conf66/adhesion/modifier/<int:pk>', login_required(views.AdhesionUpdateView.as_view()), name="adhesion_modifier"),
    path(r'conf66/adhesion/supprimer/<int:pk>', login_required(views.AdhesionDeleteView.as_view()), name="adhesion_supprimer"),

     ]
