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
    1. Add an import:  from vote__ import urls as vote_urls
    2. Add a URL to urlpatterns:  re_path(r'^vote__/', include(vote_urls))
"""
from django.urls import path, include, re_path
from . import views#, views_wizard
from django.contrib.auth.decorators import login_required


app_name = 'vote'

urlpatterns = [
    re_path(r'^$', views.accueil, name="accueil"),
    path(r'suffrages/', login_required(views.ListeSuffrages.as_view(), login_url='/auth/login/'), name="index"),
    re_path(r'^suffrage/(?P<slug>[-\w]+)$', views.lireSuffrage, name='lireSuffrage'),
    re_path(r'^modifierSuffrage/(?P<slug>[-\w]+)$', login_required(views.ModifierSuffrage.as_view(), login_url='/auth/login/'), name='modifierSuffrage'),
    re_path(r'^supprimerSuffrage/(?P<slug>[-\w]+)$',
        login_required(views.SupprimerSuffrage.as_view(), login_url='/auth/login/'), name='supprimerSuffrage'),

    path(r'ajouterSuffrage/<str:article_slug>', login_required(views.ajouterSuffrage), name='ajouterSuffrage'),
    re_path(r'^voter/(?P<slug>[-\w]+)$', login_required(views.voter), name='voter'),
    re_path(r'^modifierVote/(?P<slug>[-\w]+)$', login_required(views.ModifierVote.as_view(), login_url='/auth/login/'), name='modifierVote'),
    re_path(r'^suffrage/resultat/(?P<slug>[-\w]+)$', views.resultatsSuffrage, name='resultatsSuffrage'),
    re_path(r'^modifierCommentaireSuffrage/(?P<id>[0-9]+)$',
        login_required(views.ModifierCommentaireSuffrage.as_view(), login_url='/auth/login/'),
        name='modifierCommentaireSuffrage'),
    re_path(r'^suivre_suffrages/$', views.suivre_suffrages, name='suivre_suffrages'),
    re_path(r'^suffrage/(?P<slug>[-\w]+)/ajouterQuestion$', views.ajouterQuestion, name='ajouterQuestion'),
    re_path(r'^suffrage/(?P<slug>[-\w]+)/ajouterQuestionB$', views.ajouterQuestionB, name='ajouterQuestionB'),
    re_path(r'^suffrage/(?P<slug>[-\w]+)/ajouterQuestionM$', views.ajouterQuestionM, name='ajouterQuestionM'),

    path(r'supprimerQuestionB/<str:slug>/<int:id_question>', views.supprimerQuestionB, name='supprimerQuestionB'),
    path(r'supprimerQuestionM/<str:slug>/<int:id_question>', views.supprimerQuestionM, name='supprimerQuestionM'),
    path(r'supprimerPropositionM/<str:slug><int:id_question>/<int:id_proposition>', views.supprimerPropositionM, name='supprimerPropositionM'),
    #re_path(r'ajouter_suffrage/$', views_wizard.SuffrageWizard.as_view()),

    path(r'ajouterSuffrage_article/<str:article_slug>', views.ajouterSuffrage_article, name='ajouterSuffrage_article'),
    path(r'ajouterSondageBinaire/<str:article_slug>', views.ajouterSondageBinaire, name='ajouterSondageBinaire'),
    path(r'ajouterVoteBinaire/<int:sondageBinaire_pk>/<str:reponse_b>/', login_required(views.ajouterVoteBinaire), name='ajouterVoteBinaire'),
    path(r'modifierSondageB/<int:pk>', login_required(views.ModifierSondageB.as_view()), name='modifierSondageB'),
    path(r'supprimerSondageB/<int:pk>', login_required(views.SupprimerSondageB.as_view()), name='supprimerSondageB'),
    path(r'get_resultatSondageB/<int:sondage_pk>', views.get_resultatSondageB, name='get_resultatSondageB'),
]
