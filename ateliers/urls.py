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
from django.urls import path
from django.urls import re_path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'ateliers'

urlpatterns = [
    path('accueil-ateliers/', views.accueil, name="acceuil"),
    path('liste/', login_required(views.ListeAteliers.as_view()), name="index_ateliers"),
    re_path(r'^atelier/(?P<slug>[-\w]+)$', views.lireAtelier_slug, name='lireAtelier'),
    re_path(r'^atelier/id/(?P<id>[-\w]+)$', views.lireAtelier_id, name='lireAtelier_id'),
    re_path(r'^atelier/inscription/(?P<slug>[-\w]+)$', views.inscriptionAtelier, name='inscriptionAtelier'),
    re_path(r'^atelier/annulerInscription/(?P<slug>[-\w]+)$', views.annulerInscription, name='annulerInscription'),
    re_path(r'^atelier/contacterParticipantsAtelier/(?P<slug>[-\w]+)$', views.contacterParticipantsAtelier, name='contacterParticipantsAtelier'),

    re_path(r'^modifierAtelier/(?P<slug>[-\w]+)$', login_required(views.ModifierAtelier.as_view(), login_url='/auth/login/'), name='modifierAtelier'),
    path('modifierCommentaire/<int:id>', login_required(views.ModifierCommentaire.as_view(), login_url='/auth/login/'), name='modifierCommentaireAtelier'),
    re_path(r'^supprimerAtelier/(?P<slug>[-\w]+)$', login_required(views.SupprimerAtelier.as_view(), login_url='/auth/login/'), name='supprimerAtelier'),
    re_path(r'^ajouterAtelier/(?P<article_slug>[-\w]+)$', login_required(views.ajouterAtelier), name='ajouterAtelier_article'),
    path('ajouterAtelier/', login_required(views.ajouterAtelier), name='ajouterAtelier'),

    path('suivre_ateliers/', views.suivre_ateliers, name='suivre_ateliers'),
    path('copierAteliers/', views.copierAteliers, name='copierAteliers'),
    path('copierAteliers_inverse/', views.copierAteliers_inverse, name='copierAteliers_inverse'),
]
