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
from django.urls import path, include
from . import views, views_phoning
from django.contrib.auth.decorators import login_required

app_name = 'adherents'

urlpatterns = [
    path('<str:asso_slug>/', login_required(views.ListeAdherents.as_view()), name="accueil"),
    path('<str:asso_slug>/accueil_admin/', views.accueil_admin, name="accueil_admin"),
    path('<str:asso_slug>/get_csv_adherents/', views.get_csv_adherents, name="get_csv_adherents"),
    path('<str:asso_slug>/get_infos_adherents_pasajour/', views.get_infos_adherents_pasajour, name="get_infos_adherents_pasajour"),
    path('<str:asso_slug>/get_infos_adherents_ajour/', views.get_infos_adherents_ajour, name="get_infos_adherents_ajour"),
    path('<str:asso_slug>/get_csv_listeMails/', views.get_csv_listeMails, name="get_csv_listeMails"),
    path(r'<str:asso_slug>/infos_adherents/<str:type_info>', views.get_infos_adherent, name="get_infos_adherent"),
    path(r'<str:asso_slug>/infos_listeMail/<int:listeMail_pk>/<str:type_info>', views.get_infos_listeMail, name="get_infos_listeMail"),

    path('<str:asso_slug>/import_csv/', views.import_adherents_ggl, name="import_csv"),
    path('<str:asso_slug>/modif_APE/', views.modif_APE, name="modif_APE"),
    path('<str:asso_slug>/normaliser_adherents/', views.normaliser_adherents, name="normaliser_adherents"),

    path(r'<str:asso_slug>/adherents/', login_required(views.ListeAdherents.as_view()), name="adherent_liste"),
    path(r'<str:asso_slug>/adherent/ajouter/', views.adherent_ajouter, name="adherent_ajouter"),
    path(r'<str:asso_slug>/adherent/ajouterLesMembresGroupe/', views.ajouterLesMembresGroupe, name="ajouterLesMembresGroupe"),
    path(r'<str:asso_slug>/adherent/detail/<int:pk>', login_required(views.AdherentDetailView.as_view()), name="adherent_detail"),
    path(r'<str:asso_slug>/adherent/monProfil', views.monProfil, name="monProfil"),
    path(r'<str:asso_slug>/adherent/modifier/<int:pk>', login_required(views.AdherentUpdateView.as_view()), name="adherent_modifier"),
    path(r'<str:asso_slug>/adherent/adherents_modifier_adresse/<int:pk>', login_required(views.AdherentAdresseUpdateView.as_view()), name="adherents_modifier_adresse"),
    path(r'<str:asso_slug>/adherent/supprimer/<int:pk>', login_required(views.AdherentDeleteView.as_view()), name="adherent_supprimer"),

    path(r'<str:asso_slug>/adhesions/', login_required(views.ListeAdhesions.as_view()), name="adhesion_liste"),
    path(r'<str:asso_slug>/adhesion/creer/<int:adherent_pk>', views.ajouterAdhesion, name="adhesion_creer"),
    path(r'<str:asso_slug>/adhesion/creer/', views.ajouterAdhesion_2, name="adhesion_creer_adherent"),
    path(r'<str:asso_slug>/adhesion/detail/<int:pk>', login_required(views.AdhesionDetailView.as_view()), name="adhesion_detail"),
    path(r'<str:asso_slug>/adhesion/modifier/<int:pk>', login_required(views.AdhesionUpdateView.as_view()), name="adhesion_modifier"),
    path(r'<str:asso_slug>/adhesion/supprimer/<int:pk>', login_required(views.AdhesionDeleteView.as_view()), name="adhesion_supprimer"),

    path(r'<str:asso_slug>/inscriptions/listesInscriptions', login_required(views.ListeInscriptionsMails.as_view()), name="inscriptionMail_liste"),
    path(r'<str:asso_slug>/inscriptions/creer/<int:adherent_pk>', views.creerInscriptionMail_adherent, name="inscriptionMail_adherent"),
    path(r'<str:asso_slug>/inscriptions/creer/', views.creerInscriptionMail, name="inscriptionMail_creer"),
    path(r'<str:asso_slug>/inscriptions/detail/<int:pk>', login_required(views.InscriptionMailDetailView.as_view()), name="inscriptionMail_detail"),
    path(r'<str:asso_slug>/inscriptions/modifier/<int:pk>', login_required(views.InscriptionMailUpdateView.as_view()), name="inscriptionMail_modifier"),
    path(r'<str:asso_slug>/inscriptions/supprimer/<int:pk>', login_required(views.InscriptionMailDeleteView.as_view()), name="inscriptionMail_supprimer"),

    path(r'<str:asso_slug>/comm_adh/modifier/<int:pk>', login_required(views.Comm_adherent_modifier.as_view()), name="comm_adherent_modifier"),
    path(r'<str:asso_slug>/comm_adh/supprimer/<int:pk>', login_required(views.Comm_adherent_supprimer.as_view()), name="comm_adherent_supprimer"),
    path(r'<str:asso_slug>/comm_adh/creer/<int:adherent_pk>', views.ajouter_comm_adh, name="ajouter_comm_adh"),

    path(r'<str:asso_slug>/listesDiffusion/', login_required(views.ListeDiffusion_liste.as_view()), name="listeDiffusion_liste"),
    path(r'<str:asso_slug>/listesDiffusion/creerListe/', views.creerListeDiffusion, name="listeDiffusion_creer"),
    path(r'<str:asso_slug>/listesDiffusion/detail/<int:pk>', login_required(views.ListeDiffusionDetailView.as_view()), name="listeDiffusion_detail"),
    path(r'<str:asso_slug>/listesDiffusion/modifier/<int:pk>', login_required(views.ListeDiffusionUpdateView.as_view()), name="listeDiffusion_modifier"),
    path(r'<str:asso_slug>/listesDiffusion/supprimer/<int:pk>', login_required(views.ListeDiffusionDeleteView.as_view()), name="listeDiffusionsupprimer"),
    path(r'<str:asso_slug>/listesDiffusion/mesListesMails/', views.mesListesMails, name="mesListesMails"),
    path(r'<str:asso_slug>/inscriptions/swap_inscription/<int:listeMail_pk>/<int:adherent_pk>',
         views.swap_inscription, name="swap_inscription"),

    path(r'<str:asso_slug>/listesDiffusion/ajouter/<int:listeDiffusion_pk>/', views.ajouterAdherentAListeDiffusion,
         name="listeDiffusion_ajouterAdherent"),
    path(r'<str:asso_slug>/listesDiffusion/ajouterMail/<int:listeDiffusion_pk>/', views.ajouterMailAListeDiffusion,
         name="listeDiffusion_ajouterMail"),
    path(r'<str:asso_slug>/inscriptions/ajouter/<int:adherent_pk>',
         views.ajouterInscription_AdherentListeDiffusion, name="ajouterInscription_AdherentListeDiffusion"),


    path(r'<str:asso_slug>/phoning/projet/liste', views_phoning.ProjetPhoning_liste.as_view(), name="phoning_projet_liste"),
    path(r'<str:asso_slug>/phoning/projet/simple/<int:projet_pk>', login_required(views_phoning.Contact_liste.as_view()), name="phoning_projet_simple"),
    path(r'<str:asso_slug>/phoning/projet/courant/simple', views_phoning.phoning_projet_courant, name="phoning_projet_courant"),
    path(r'<str:asso_slug>/phoning/projet/courant/complet', login_required(views_phoning.Contact_liste.as_view()), name="phoning_projet_complet"),
    path(r'<str:asso_slug>/phoning/projet/complet/<int:projet_pk>', login_required(views_phoning.Contact_liste.as_view()), name="phoning_projet_complet"),
    #path(r'phoning/contact_ajouter/', views.creerListeDiffusion, name="listeDiffusion_creer"),
    path(r'<str:asso_slug>/phoning/ajouter/acceuil', views_phoning.contact_ajouter_accueil, name="phoning_contact_outils"),
    path(r'<str:asso_slug>/phoning/projet/courant/ajouter', login_required(views_phoning.Contact_ajouter.as_view()), name="phoning_contact_ajouter"),
    path(r'<str:asso_slug>/phoning/projet/courant/ajouter/listetel', views_phoning.phoning_contact_ajouter_listetel, name="phoning_contact_ajouter_listetel"),
    path(r'<str:asso_slug>/phoning/ajouter/csv', views_phoning.phoning_contact_ajouter_csv, name="phoning_contact_ajouter_csv"),
    path(r'<str:asso_slug>/phoning/ajouter/csv_inversernomprenom', views_phoning.phoning_contact_ajouter_csv_inversernomprenom, name="phoning_csv_inversernomprenom"),
    path(r'<str:asso_slug>/phoning/ajouter/csv_editNonVotants', views_phoning.phoning_contact_ajouter_csv_editNonVotants, name="phoning_csv_editNonVotants"),
    path(r'<str:asso_slug>/phoning/ajouter/csv_viti', views_phoning.phoning_contact_ajouter_csv_viti, name="phoning_csv_viti"),
    path(r'<str:asso_slug>/phoning/ajouter/adherents', views_phoning.ajouterAdherents, name="phoning_ajouterAdherents"),
    path(r'<str:asso_slug>/phoning/ajouter/membresGroupe', views_phoning.ajouterMembresGroupe, name="phoning_ajouterMembresGroupe"),
    path(r'<str:asso_slug>/phoning/supprimer/doublons', views_phoning.supprimer_doublons, name="phoning_supprimer_doublons"),
    path(r'<str:asso_slug>/phoning/supprimer/nettoyer_telephones', views_phoning.nettoyer_telephones, name="nettoyer_telephones"),
    path(r'<str:asso_slug>/phoning/supprimer/nettoyer_noms', views_phoning.nettoyer_noms, name="nettoyer_noms"),
    path(r'<str:asso_slug>/phoning/modifier/<int:pk>', login_required(views_phoning.Contact_modifier.as_view()), name="phoning_contact_modifier"),
    path(r'<str:asso_slug>/phoning/supprimer/<int:pk>', login_required(views_phoning.Contact_supprimer.as_view()), name="phoning_contact_supprimer"),
    path(r'<str:asso_slug>/phoning/supprimer2/<int:contact_pk>', views_phoning.contact_supprimer, name="phoning_contact_supprimer2"),
    path(r'<str:asso_slug>/phoning/contact/ajouter/<int:contact_pk>', views_phoning.contactContact_ajouter, name="phoning_contact_contact_ajout"),
    path(r'<str:asso_slug>/phoning/contact/supprimer/<int:contact_contact_pk>', views_phoning.contactContact_supprimer, name="phoning_contact_contact_supprimer"),
    path(r'<str:asso_slug>/phoning/get_csv_contacts/', views_phoning.get_csv_contacts, name="get_csv_contacts"),


    path(r'<str:asso_slug>/phoning/projet/ajouter', login_required(views_phoning.ProjetPhoning_ajouter.as_view()), name="phoning_projet_ajouter"),
    path(r'<str:asso_slug>/phoning/projet/<int:pk>/modifier', login_required(views_phoning.ProjetPhoning_modifier.as_view()), name="phoning_projet_modifier"),
    path(r'<str:asso_slug>/phoning/projet/<int:pk>/supprimer', login_required(views_phoning.ProjetPhoning_supprimer.as_view()), name="phoning_projet_supprimer"),

    path(r'<str:asso_slug>/phoning/projet/<int:pk>/ajax_infocontact', views_phoning.ajax_infocontact, name="phoning_ajax_infocontact"),
    path(r'<str:projet_pk>/infos_contacts/<str:type_info>', views.get_infos_contacts, name="get_infos_contacts"),

    path(r'<str:asso_slug>/admin_restaurerAdherents', views.admin_restaurerAdherents, name="admin_restaurerAdherents"),
]
