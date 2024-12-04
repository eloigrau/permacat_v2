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
    1. Add an import:  from jardinpartage__ import urls as jardinpartage_urls
    2. Add a URL to urlpatterns:  re_path(r'^jardinpartage__/', include(jardinpartage_urls))
"""
from django.urls import path, include, re_path
from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'jardinpartage'

urlpatterns = [
    re_path(r'^accueil/$', views.accueil, name="forum"),
    re_path(r'^articles/$', login_required(views.ListeArticles.as_view(), login_url='/auth/login/'), name="index"),
    path(r'articles/<str:jardin>', login_required(views.ListeArticles_jardin.as_view(), login_url='/auth/login/'), name="index_jardin"),
    # re_path(r'^newPost/', views.ajouterArticle, name='ajouterArticle'),
    # re_path(r'^article/(?P<slug>.+)$', views.lire, name='lire'),

    re_path(r'^article/(?P<slug>[-\w]+)$', views.lireArticle, name='lireArticle'),
    re_path(r'^accepter_participation$', views.accepter_participation, name='accepter_participation'),
    re_path(r'^modifierArticle/(?P<slug>[-\w]+)$', login_required(views.ModifierArticle.as_view(), login_url='/auth/login/'), name='modifierArticle'),
    re_path(r'^suiveursArticle/(?P<slug>[-\w]+)$', views.articles_suivis, name='suiveursArticle'),
    re_path(r'^suiveursArticles/$', views.articles_suiveurs, name='suiveursArticles'),
    re_path(r'^supprimerArticle/(?P<slug>[-\w]+)$', login_required(views.SupprimerArticle.as_view(), login_url='/auth/login/'), name='supprimerArticle'),
    re_path(r'^ajouterArticle/$', login_required(views.ajouterArticle), name='ajouterNouvelArticle'),

    re_path(r'^suivre_article/(?P<slug>[-\w]+)/$', views.suivre_article, name='suivre_article'),
    re_path(r'^suivre_articles/$', views.suivre_articles, name='suivre_articles'),

    re_path(r'^modifierCommentaireArticle/(?P<id>[0-9]+)$',
        login_required(views.ModifierCommentaireArticle.as_view(), login_url='/auth/login/'),
        name='modifierCommentaireArticle'),

    re_path(r'ajouterEvenement/$', views.ajouterEvenement, name='ajouterEvenement'),
    path(r'ajouterEvenementArticle/<str:slug_article>', views.ajouterEvenementArticle, name='ajouterEvenementArticle'),

]
