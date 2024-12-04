# -*- coding: utf-8 -*-
"""bourseLibre URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  re_path(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  re_path(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog__ import urls as blog_urls
    2. Add a URL to urlpatterns:  re_path(r'^blog__/', include(blog_urls))
"""
from django.urls import path, include, re_path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'fiches'

urlpatterns = [
    re_path(r'^accueil-fiches/$', login_required(views.accueil), name="acceuil"),
    re_path(r'^fiches/$', login_required(views.ListeFiches.as_view(), login_url='/auth/login/'), name="index"),
    re_path(r'^ateliers/$', login_required(views.ListeAteliers.as_view(), login_url='/auth/login/'), name="index_ateliers"),
    re_path(r'^fiche/(?P<slug>[-\w]+)$', views.lireFiche, name='lireFiche'),
    re_path(r'^atelier/(?P<slug>[-\w]+)$', views.lireAtelier, name='lireAtelier'),
    re_path(r'^atelier/id/(?P<id>[-\w]+)$', views.lireAtelier_id, name='lireAtelier_id'),
    re_path(r'^modifierFiche/(?P<slug>[-\w]+)$', login_required(views.ModifierFiche.as_view(), login_url='/auth/login/'), name='modifierFiche'),
    re_path(r'^modifierAtelier/(?P<slug>[-\w]+)$', login_required(views.ModifierAtelier.as_view(), login_url='/auth/login/'), name='modifierAtelier'),
    re_path(r'^supprimerFiche/(?P<slug>[-\w]+)$', login_required(views.SupprimerFiche.as_view(), login_url='/auth/login/'), name='supprimerFiche'),
    re_path(r'^ajouterFiche/$', login_required(views.ajouterFiche), name='ajouterFiche'),
    re_path(r'^ajouterAtelier/(?P<fiche_slug>[-\w]+)$', login_required(views.ajouterAtelier), name='ajouterAtelier'),
    re_path(r'^voirFicheTest/$', views.voirFicheTest, name='voirFicheTest'),

]
