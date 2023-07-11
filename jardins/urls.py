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
    url(r'^$', views.accueil, name="accueil"),

    ## plantes
    url(r'^accueil_admin/$', views.accueil_admin, name="accueil_admin"),
    url(r'^import_db_inpn_0/$', views.import_db_inpn_0, name="import_db_inpn_0"),
    url(r'^import_db_inpn_1/$', views.import_db_inpn_1, name="import_db_inpn_1"),
    url(r'^import_db_inpn_2/$', views.import_db_inpn_2, name="import_db_inpn_2"),
    url(r'^import_db_inpn_3/$', views.import_db_inpn_3, name="import_db_inpn_3"),
    url(r'^import_db_inpn_4/$', views.import_db_inpn_4, name="import_db_inpn_4"),
    url(r'^import_grainotheque_rtg_1/$', views.import_grainotheque_rtg_1, name="import_grainotheque_rtg_1"),
    url(r'^import_grainotheque_rtg_2/$', views.import_grainotheque_rtg_2, name="import_grainotheque_rtg_2"),
    path(r'plantes/', views.ListePlantes.as_view(), name="plantes"),
    path(r'voir_plante/<str:cd_nom>', views.voir_plante, name="voir_plante"),
    path(r'voir_plante_nom/', views.voir_plante_nom, name="voir_plante_nom"),
    path(r'voir_plante_recherche/', views.voir_plante_recherche, name="voir_plante_recherche"),
    url(r'^plante-ac/$', login_required(views.PlanteAutocomplete.as_view(), login_url='/auth/login/'), name='plante-ac',),
    url(r'^ajouterPlante/$', views.ajouter_plante, name="ajouter_plante"),
    url(r'^chercher_plante/$', views.chercher_plante, name="chercher_plante"),

    ##jardins
    path(r'jardins/carte/', views.carte_jardins, name="carte_jardins"),
    path(r'jardiniers/carte/', views.carte_jardiniers, name="carte_jardiniers"),
    path(r'grainotheques/carte/', views.carte_graino, name="carte_graino"),

    path(r'jardin/ajouter/', login_required(views.AjouterJardin.as_view()), name="jardin_ajouter"),
    path(r'jardin/jardin_ajouterAdresse/<str:slug>', views.jardin_ajouterAdresse, name="jardin_ajouterAdresse"),
    path(r'jardin/modifierAdresse/<str:slug>', views.jardin_modifierAdresse, name="jardin_modifierAdresse"),
    path(r'jardin/modifier/<str:slug>', login_required(views.ModifierJardin.as_view()), name="jardin_modifier"),
    path(r'jardin/jardin_supprimer/<str:slug>', login_required(views.SupprimerJardin.as_view()), name="jardin_supprimer"),
    path(r'jardin/voir/<str:slug>', login_required(views.JardinDetailView.as_view()), name="jardin_lire"),

    path(r'jardin/inscription/<str:slug>', views.inscriptionJardin, name='inscriptionJardin'),
    path(r'jardin/annulerInscription/<str:slug>', views.annulerInscription, name='annulerInscription'),
    path(r'jardin/contacterInscritsJardin/<str:slug>', views.contacterInscritsJardin, name='contacterInscritsJardin'),

    path(r'grainotheque/ajouter/', login_required(views.AjouterGrainotheque.as_view()), name="grainotheque_ajouter"),
    path(r'grainotheque/modifier/<str:slug>', login_required(views.ModifierGrainotheque.as_view()), name="grainotheque_modifier"),
    path(r'grainotheque/editInfosGraine/<int:pk>', login_required(views.ModifierInfoGraine.as_view()), name="grainotheque_editInfosGraine"),
    path(r'jardin/supprimer_grainotheque/<str:slug>', login_required(views.SupprimerGrainotheque.as_view()), name="grainotheque_supprimer"),
    path(r'grainotheque/voir/<str:slug>', login_required(views.GrainothequeDetailView.as_view()), name="grainotheque_lire"),
    path(r'grainotheque/ajouterGraine/<str:slug>', views.graino_ajouterGraine, name="graino_ajouterGraine"),
    path(r'grainotheque/modifierGraine/<str:slug_graino>/<int:pk>', views.graino_modifierGraine, name="graino_modifierGraine"),
    path(r'grainotheque/ajouterAdresse/<str:slug>', views.grainotheque_ajouterAdresse, name="grainotheque_ajouterAdresse"),
    path(r'grainotheque/modifierAdresse/<str:slug>', views.grainotheque_modifierAdresse, name="grainotheque_modifierAdresse"),
    path(r'grainotheque/supprimerGraines/<str:slug>', views.grainotheque_supprimerGraines, name="grainotheque_supprimerGraines"),
    ]
