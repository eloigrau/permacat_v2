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
from . import views, views_base, views_notifications, views_admin, views_ajax, views_inscriptions
from .helloasso import apiHA_pcat
from django.views.generic import TemplateView

# On import les vues de Django, avec un nom spécifique
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView
from django.urls import reverse_lazy
from django.contrib import admin
from .settings import MEDIA_ROOT, MEDIA_URL, LOCALL
from django.conf.urls.static import static
from django.conf.urls.i18n import path
from django.views.static import serve

admin.sites.site_header ="Admin"
admin.sites.site_title ="Admin Permacat"

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),  # Language switching
    re_path(r'^summernote/', include('local_summernote.urls')),
    # path('tinymce/', include('tinymce.urls')),
    # re_path(r'^.well-known/acme-challenge/', include('acme_challenge.urls')),
    # path('newsletter/', include('newsletter.urls')),
    # re_path(r'^chat/', include('chat.urls')),
    path(r'agenda/', include('cal.urls')),
    path(r'agoratransition/', include('agoratransition.urls', namespace='agoratransition')),
    path(r'ducepaujus/', include('ducepaujus.urls', namespace='ducepaujus')),
    path(r'permagora/plateforme/', include('permagora.urls', namespace='permagora')),
    path(r'defraiement/', include('defraiement.urls', 'defraiement')),
    path(r'carto/', include('carto.urls')),
    path(r'jardins/', include('jardins.urls')),
    path(r'permagora/', include('permagorapresentation.urls', namespace='permagorapresentation')),
    path(r'adherents/', include('adherents.urls', namespace='adherents')),
    path(r'photolog/', include('photologue.urls', namespace='photologue')),
    path('qr_code/', include('qr_code.urls', namespace="qr_code")),
#    path(r'phonebook/', include('phonebook.urls')),
    re_path('^', include('django.contrib.auth.urls')),
    re_path('avatar/', include('avatar.urls')),
    #path('ledger/', include('django_ledger.urls', namespace='django_ledger')),
    path('captcha/', include('local_captcha.urls')),
    #path("r/", include("urlshortner.urls")),
    path(r'webpush/', include('webpush.urls')),
    re_path(r'^$', views.bienvenue, name='bienvenue'),
    re_path(r'^bienvenue/$', views.bienvenue, name='bienvenue'),
    re_path(r'^faq/$', views_base.faq, name='faq'),
    re_path(r'^gallerie/$', views_base.gallerie, name='gallerie'),
    path(r'admin_asso/<str:asso>', views.admin_asso, name='admin_asso'),
    re_path(r'^media/(?P<path>.*)', views.accesfichier, name='accesfichier'),

    path(r'fichiers/asso/<str:asso>', views.telechargements_asso, name='telechargements_asso'),
    re_path(r'^notifications/parType/$', views_notifications.notifications, name='notifications'),
    re_path(r'^notifications/activite/$', views_notifications.notifications_news_regroup, name='notifications_news'),
    re_path(r'^notifications/parDate/$', views_notifications.notificationsParDate, name='notificationsParDate'),
    re_path(r'^notifications/parGroupe/$', views_notifications.notificationsParGroupe, name='notificationsParGroupe'),
    path(r'notifications/Lues/<str:temps>', views_notifications.notificationsLues, name='notificationsLues'),
    re_path(r'^notificatioadherent_assos/changerDateNotif/$', views_notifications.changerDateNotif, name='changerDateNotif'),
    re_path(r'^notifications/notif_cejour/$', views_notifications.notif_cejour, name='notif_cejour'),
    re_path(r'^notifications/notif_hier/$', views_notifications.notif_hier, name='notif_hier'),
    re_path(r'^notifications/notif_cettesemaine/$', views_notifications.notif_cettesemaine, name='notif_cettesemaine'),
    re_path(r'^notifications/notif_cemois/$', views_notifications.notif_cemois, name='notif_cemois'),
    re_path(r'^notifications/visites/', views_notifications.voirDerniersArticlesVus, name='articles_visites'),
    re_path(r'^dernieresInfos/$', views_notifications.dernieresInfos, name='dernieresInfos'),
    re_path(r'^prochaines_rencontres/$', views.prochaines_rencontres, name='prochaines_rencontres'),
    path(r'presentation/<str:asso>/', views.presentation_asso, name='presentation_asso'),
    path(r'presentation/citealtruiste/organisation', views.organisation_citealt, name='organisation_citealt'),
    path(r'groupes/presentation/', views.presentation_groupes, name='presentation_groupes'),
    path(r'permagora/inscription/', views_inscriptions.inscription_permagora, name='inscription_permagora'),
    path(r'citealtruiste/inscription/', views_inscriptions.inscription_citealt, name='inscription_citealt'),
    path(r'projetBzzz/inscription/', views_inscriptions.inscription_bzz2022, name='inscription_bzz2022'),
    path(r'viure/inscription/', views_inscriptions.inscription_viure, name='inscription_viure'),
    path(r'asso/inscription/<str:asso_slug>', views_inscriptions.inscription_asso, name='inscription_asso'),
    path(r'jardins/inscription/', views_inscriptions.inscription_jp, name='inscription_jp'),
    re_path(r'^site/presentation/$', views_base.presentation_site, name='presentation_site'),
    re_path(r'^site/pourquoi/$', views_base.presentation_site_pkoi, name='presentation_site_pkoi'),
    re_path(r'^site/conseils/$', views_base.presentation_site_conseils, name='presentation_site_conseils'),
    re_path(r'^permacat/statuts/$', views_base.statuts, name='statuts'),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    re_path(r'^gestion/', admin.site.urls, name='admin',),

    # re_path(r'^ramenetagraine/statuts/$', views.statuts_rtg, name='statuts_rtg'),
    # re_path(r'^jet/', include('jet.urls')),  # Django JET URLS
    # re_path(r'^jet/dashboard/', include('jet.dashboard.urls')),  # Django JET dashboard URLS
    # re_path(r'^admin/', admin.site.urls),

    re_path(r'^merci/$', views.merci, name='merci'),
    re_path(r'^forum/', include('blog.urls', namespace='bourseLibre.blog')),
    # re_path(r'^jardins/', include('jardinpartage.urls', namespace='bourseLibre.jardinpartage')),
    # re_path(r'^agora/', include('agoratransition.urls', namespace='bourseLibre.agoratransition')),
    re_path(r'^vote/', include('vote.urls', namespace='bourseLibre.vote')),
    re_path(r'^switchThemeSombre/', views.switchThemeSombre, name='switchThemeSombre'),
    re_path(r'^switchLanguage/', views.switchLanguage, name='switchLanguage'),

    re_path(r'^kit/', include('fiches.urls', namespace='bourseLibre.fiches')),
    re_path(r'^ateliers/', include('ateliers.urls', namespace='bourseLibre.ateliers')),
    re_path(r'^chercher/$', login_required(views.chercher), name='chercher'),
    re_path(r'^chercher/forum/$', login_required(views.chercher_articles), name='chercher_articles'),
    re_path(r'^chercher/annonces/$', login_required(views.chercher_annonces), name='chercher_annonces'),
    re_path(r'^chercher/altermarche/$', login_required(views.chercher_produits), name='chercher_produits'),
    re_path(r'^compte/profil/(?P<user_id>[0-9]+)/$', login_required(views.profil), name='profil',),
    re_path(r'^compte/profil/(?P<user_username>[\w.@+-]+)/$', login_required(views_base.profil_nom), name='profil_nom',),
    re_path(r'^compte/profile/$',  login_required(views.profil_courant), name='profil_courant',),
    re_path(r'^compte/profil_inconnu/$', views_base.profil_inconnu, name='profil_inconnu',),
    re_path(r'^compte/profil_modifier/$', login_required(views.profil_modifier.as_view()), name='profil_modifier',),
    re_path(r'^compte/profil_supprimer/$', login_required(views.profil_supprimer.as_view()), name='profil_supprimer',),
    re_path(r'^compte/profil_modifier_adresse/$', login_required(views.profil_modifier_adresse), name='profil_modifier_adresse',),
    path('compte/modifier_adresse/<int:adresse_pk>', login_required(views.modifier_adresse), name='modifier_adresse',),
    path('compte/supprimer_adresse/<int:adresse_pk>', login_required(views.supprimer_adresse), name='supprimer_adresse',),
    re_path(r'^compte/profil_modifier_adresse_user/(?P<user_pk>[0-9]+)/$', login_required(views.profil_modifier_adresse_user), name='profil_modifier_adresse_user',),
    re_path(r'^compte/profil_contact/(?P<user_id>[0-9]+)/$', login_required(views.profil_contact), name='profil_contact',),
    re_path(r'^compte/mesSuivis/$', login_required(views.mesSuivis), name='mesSuivis',),
    re_path(r'^compte/supprimerAction/(?P<actionid>[0-9]+)/$', login_required(views.supprimerAction), name='supprimerAction',),
    re_path(r'^compte/mesActions/$', login_required(views.mesActions), name='mesActions',),
    path(r'compte/mesPublications/<str:type_action>', login_required(views.mesPublications), name='mesPublications',),
    path(r'compte/ajouterAdhesion/<str:slugAsso>', login_required(views_admin.ajouterAdhesion), name='ajouterAdhesion',),
    re_path(r'^compte/activite/(?P<pseudo>[\w.@+-]+)/$', login_required(views_base.activite), name='activite',),
    re_path(r'^register/$', views.register, name='senregistrer',),
    re_path(r'^reset-password/$', PasswordResetView.as_view(template_name='accounts/reset_password.html',
                                  email_template_name='accounts/reset_password_email.html',
                                  success_url=reverse_lazy('bienvenue')), name='reset_password'),
    # re_path(r'^password/reset/$', views.reset_password, name='reset_password'),
    re_path(r'^password/change/$', views.change_password, name='change_password'),
    path('auth/', include('django.contrib.auth.urls')),

    re_path(r'^contact_admins/$', views.contact_admins, name='contact_admins',),
    re_path(r'^signaler_bug/$', views.signaler_bug, name='signaler_bug',),
    re_path(r'^charte/$', views_base.charte, name='charte',),
    re_path(r'^cgu/$', views_base.cgu, name='cgu',),
    re_path(r'^liens/$', views_base.liens, name='liens',),
    path(r'fairedon/<str:asso>/', views.fairedon_asso, name='faire_don',),
    path(r'adhesion/<str:asso>/', views.adhesion_asso, name='adhesion_asso'),
    path(r'adhesion/', views.adhesion_entree, name='adhesion_entree'),
    path(r'adhesion/adhesion_asso_modifier/<int:pk>', views.Adhesion_asso_modifier.as_view(), name='adhesion_asso_modifier'),
    path(r'adhesion/adhesion_asso_supprimer/<int:pk>', views.Adhesion_asso_supprimer.as_view(), name='adhesion_asso_supprimer'),
    # re_path(r'^agenda/$', views.agenda, name='agenda',),
    path(r'annuaire/<str:asso>', login_required(views.annuaire), name='annuaire',),
    path(r'cooperateurs/listeAdhesions/<str:asso>', login_required(views.listeAdhesions), name='listeAdhesions',),
    path(r'cooperateurs/listeContacts/<str:asso>', login_required(views.listeContacts), name='listeContacts',),
    path(r'cooperateurs/listeContacts_admin/', login_required(views.listeContacts_admin), name='listeContacts_admin',),
    path(r'cooperateurs/listeFollowers/<str:asso>', login_required(views.listeFollowers), name='listeFollowers',),
    path(r'cooperateurs/carte/<str:asso>', login_required(views.carte), name='carte',),

    re_path(r'^cooperateurs/contacter_newsletter/$', login_required(views_inscriptions.contacter_newsletter), name='contacter_newsletter',),
    re_path(r'^cooperateurs/contacter_adherents/$', login_required(views_inscriptions.contacter_adherents), name='contacter_adherents',),

    re_path(r'^marche/proposer/(?P<type_produit>[-A-Za-z]+)/$', login_required(views.produit_proposer), name='produit_proposer', ),
    re_path(r'^marche/proposer/', login_required(views.proposerProduit_entree), name='produit_proposer_entree',),

    # re_path(r'^list$', views.product_list),
    # re_path(r'^list2/$', FilterView.as_view(model=Produit, filterset_class=ProductFilter,)),
    re_path(r'^marche/$', login_required(views.ListeProduit.as_view()),  name="marche"),
    re_path(r'^marche/lister/$', login_required(views.ListeProduit.as_view()),  name="marche"),
    re_path(r'^marche/supprimerProduits_expires_confirmation/$', views.supprimerProduits_expires_confirmation,  name="supprimerProduits_expires_confirmation"),
    re_path(r'^marche/supprimerProduits_expires/$', views.supprimerProduits_expires,  name="supprimerProduits_expires"),
    re_path(r'^marche/lister_offres/', login_required(views.ListeProduit_offres.as_view()),
        name="marche_offres"),
    re_path(r'^marche/lister_recherches/', login_required(views.ListeProduit_recherches.as_view()),
        name="marche_recherches"),

    re_path(r'^marche/detail/(?P<produit_id>[0-9]+)/$', login_required(views.detailProduit), name='produit_detail',),

    re_path(r'^marche/modifier/(?P<pk>[0-9]+)/$',
        login_required(views.ProduitModifier.as_view()), name='produit_modifier', ),
    re_path(r'^marche/contacterProducteur/(?P<producteur_id>[0-9]+)/$',
        login_required(views.produitContacterProducteur), name='produit_contacterProducteur', ),
    re_path(r'^marche/supprimer/(?P<pk>[0-9]+)/$',
        login_required(views.ProduitSupprimer.as_view()), name='produit_supprimer', ),

    re_path(r'^panier/afficher/$', login_required(views.afficher_panier), name='panier_afficher', ),
    re_path(r'^panier/ajouter/(?P<produit_id>[0-9]+)/(?P<quantite>[0-9]{1,3}([.]{0,1}[0-9]{0,3}))/$',
        login_required(views.ajouterAuPanier), name='produit_ajouterAuPanier', ),
    re_path(r'^panier/supprimerItem/(?P<item_id>[0-9]+)',
        login_required(views.enlever_du_panier), name='supprimerDuPanier', ),
    re_path(r'^requetes/afficher/$',
        login_required(views.afficher_requetes), name='afficher_requetes', ),

    re_path(r'^conversations/(?P<destinataire>[\w.@+-]+)$', login_required(views.lireConversation), name='agora_conversation'),
    re_path(r'^conversations/(?P<destinataire1>[\w.@+-]+)/(?P<destinataire2>[\w.@+-]+)$', login_required(views.lireConversation_2noms), name='lireConversation_2noms'),
    re_path(r'^conversations/$', login_required(views.ListeConversations.as_view()), name='conversations'),
    re_path(r'^conversations/chercher/$', login_required(views.chercherConversation), name='chercher_conversation'),
    re_path(r'^conversations/profil_ac/$', login_required(views.ProfilAutocomplete.as_view(), login_url='/auth/login/'), name='profil_ac'),
    re_path(r'^conversations/profil_ac2/$', login_required(views.ProfilAutocomplete2.as_view(), login_url='/auth/login/'), name='profil_ac2'),
    path(r'conversations/profil_autocomplete_recherche/', views.profil_autocomplete_recherche, name="profil_autocomplete_recherche"),
    #path(r'salons/profil_autocomplete_recherche/', views.profil_autocomplete_recherche_salon, name="profil_autocomplete_recherche_salon"),

    re_path(r'^suivre_conversation/$', views_inscriptions.suivre_conversations, name='suivre_conversations'),
    re_path(r'^suivre_produits/$', views_inscriptions.suivre_produits, name='suivre_produits'),
    re_path(r'^sereabonner/$', views_inscriptions.sereabonner, name='sereabonner'),
    re_path(r'^sedesabonner/$', views_inscriptions.sedesabonner, name='sedesabonner'),
    re_path(r'^sedesabonner_particuliers/$', views_inscriptions.sedesabonner_particuliers, name='sedesabonner_particuliers'),
    re_path(r'^sereabonner_salons/$', views_inscriptions.sereabonner_salons, name='sereabonner_salons'),
    re_path(r'^sedesabonner_salons/$', views_inscriptions.sedesabonner_salons, name='sedesabonner_salons'),
    re_path(r'^reinitialiserTousMesAbonnement/$', views_inscriptions.reinitialiserTousMesAbonnement, name='reinitialiserTousMesAbonnement'),
    re_path(r'^supprimerTousMesAbonnement/$', views_inscriptions.supprimerTousMesAbonnement, name='supprimerTousMesAbonnement'),
    path(r'agora/<str:asso>', login_required(views.agora), name='agora'),
    path(r'suivre_agora/<str:asso>', views_inscriptions.suivre_agora, name='suivre_agora'),
    path(r'salon/accueil', login_required(views.salon_accueil), name='salon_accueil'),
    path(r'salon/d/<str:slug>', login_required(views.salon), name='salon'),
    path(r'modifierSalon/<str:slug>', login_required(views.modifierSalon), name='modifierSalon'),
    path(r'creerSalon/', login_required(views.creerSalon), name='creerSalon'),
    re_path(r'^salons/$', login_required(views.ListeSalons.as_view()),  name="salons"),
    path(r'suivre_salon/<str:slug_salon>', views_inscriptions.suivre_salon, name='suivre_salon'),
    path(r'inviterDansSalon/<str:slug_salon>', views.inviterDansSalon, name='inviterDansSalon'),
    path(r'invitationDansSalon/<str:slug_salon>', views.invitationDansSalon, name='invitationDansSalon'),
    path(r'sortirDuSalon/<str:slug_salon>', views.sortirDuSalon, name='sortirDuSalon'),
    re_path(r'ajouterEvenementSalon/(?P<slug_salon>[-\w]+)$', views.ajouterEvenementSalon, name='ajouterEvenementSalon'),
    re_path(r'^supprimerEvenementSalon/(?P<slug_salon>[-\w]+)-(?P<id_evenementSalon>[0-9]+)$',
        login_required(views.SupprimerEvenementSalon.as_view(), login_url='/auth/login/'),
        name='supprimerEvenementSalon'),

    path(r'sortirDuSalon/<str:slug_salon>', views.sortirDuSalon, name='sortirDuSalon'),
    re_path(r'^activity/', include('actstream.urls')),

    path(r'partagerPosition/<str:slug_conversation>', views.partagerPosition, name='partagerPosition'),
    path(r'voirLieu/<str:id_lieu>', views.voirLieu, name='voirLieu'),
#    path(r'wiki_ecovillage_notifications/', include('django_nyt.urls')),
#    path(r'wiki_ecovillage/', include('wiki.urls')),

    path(r'compte/mesFavoris/', views.Favoris_list.as_view(), name='mesFavoris', ),
    path(r'compte/favoris/ajouter/', login_required(views.favoris_ajouter), name='favoris_ajouter' ),
    path(r'compte/favoris/ajouter/ajax/', views_ajax.ajax_ajouterFavoris, name='favoris_ajouterPage_ajax'),
    path(r'compte/favoris/ajouter/modal/', views_ajax.modal_ajouterFavoris, name='favoris_ajouterPage_modal'),
    path(r'compte/favoris/supprimer/<int:pk>', views.Favoris_supprimer.as_view(), name='favoris_delete' ),
    path(r'compte/favoris/update/<int:pk>', views.Favoris_update.as_view(), name='favoris_update' ),

    re_path(r'^inscription_newsletter/$', views_inscriptions.inscription_newsletter, name='inscription_newsletter', ),
    re_path(r'^desinscription_newsletter/$', views_inscriptions.desinscription_newsletter, name='desinscription_newsletter', ),
    path(r'admin/modifier_message/<int:id>/<str:type_msg>/<str:asso>',  login_required(views.ModifierMessageAgora.as_view()), name='modifierMessage'),
    re_path(r'^admin/voirEmails/$', views_admin.voirEmails,  name="voirEmails"),
    re_path(r'^admin/nettoyerActions/$', views_admin.nettoyerActions,  name="nettoyerActions"),
    re_path(r'^admin/nettoyerFollows/$', views_admin.nettoyerFollows,  name="nettoyerFollows"),
    re_path(r'^admin/nettoyerFollowsValide/$', views_admin.nettoyerFollowsValide,  name="nettoyerFollowsValide"),
    re_path(r'^admin/nettoyerFollowsValideUser/$', views_admin.nettoyerFollowsValideUser,  name="nettoyerFollowsValideUser"),
    re_path(r'^admin/nettoyerHistoriqueAdmin/$', views_admin.nettoyerHistoriqueAdmin,  name="nettoyerHistoriqueAdmin"),
    re_path(r'^admin/nettoyerAdresses/$', views_admin.nettoyerAdresses,  name="nettoyerAdresses"),
    re_path(r'^admin/envoyerEmailsRequete/$', views_admin.envoyerEmailsRequete,  name="envoyerEmailsRequete"),
    re_path(r'^admin/envoyerEmailsTest/$', views_admin.envoyerEmailsTest,  name="envoyerEmailsTest"),
    re_path(r'^admin/voir_articles_a_archiver/$', views_admin.voir_articles_a_archiver,  name="voir_articles_a_archiver"),
    re_path(r'^admin/archiverArticles/$', views_admin.archiverArticles,  name="archiverArticles"),
    re_path(r'^admin/voirPbProfils/$', views_admin.voirPbProfils,  name="voirPbProfils"),
    path(r'admin/decalerEvenements/<int:num>', views_admin.decalerEvenements,  name="decalerEvenements"),
    re_path(r'^admin/abonnerAdherentsCiteAlt/$', views_admin.abonnerAdherentsCiteAlt,  name="abonnerAdherentsCiteAlt"),
    re_path(r'^admin/creerAction_articlenouveau/$', views_admin.creerAction_articlenouveau,  name="creerAction_articlenouveau"),
    re_path(r'^admin/supprimervieuxcomptes/$', views_admin.supprimervieuxcomptes,  name="supprimervieuxcomptes"),
    re_path(r'^admin/envoyerMailVieuxComptes/$', views_admin.envoyerMailVieuxComptes,  name="envoyerMailVieuxComptes"),
    re_path(r'^admin/envoiNewsletter2023/$', views_admin.envoiNewsletter2023,  name="envoiNewsletter2023"),
    re_path(r'^admin/supprimerHitsAnciens/$', views_admin.supprimerHitsAnciens,  name="supprimerHitsAnciens"),
    re_path(r'^admin/supprimerActionsAnciens/$', views_admin.supprimerActionsAnciens,  name="supprimerActionsAnciens"),
    re_path(r'^admin/transforBlogJpToForum/$', views_admin.transforBlogJpToForum,  name="transforBlogJpToForum"),
    re_path(r'^admin/movePermagoraInscritsToNewsletter/$', views_admin.movePermagoraInscritsToNewsletter,  name="movePermagoraInscritsToNewsletter"),
    re_path(r'^admin/reinitialiserAbonnementsPermAgora/$', views_admin.reinitialiserAbonnementsPermAgora,  name="reinitialiserAbonnementsPermAgora"),
    path('admin/inscrireProfilAuGroupe/<int:id_profil>/<str:asso_slug>', views_admin.inscrireProfilAuGroupe,  name="inscrireProfilAuGroupe"),
    path('admin/associerProfil_adherent/<str:asso_slug>/<int:profil_pk>/', views_admin.associerProfil_adherent,  name="associerProfil_adherent"),
    path('admin/reabonner_tous_profils/', views_admin.reabonner_tous_profils,  name="reabonner_tous_profils"),
    path('admin/envoyer_emails_reabonnement/', views_admin.envoyer_emails_reabonnement,  name="envoyer_emails_reabonnement"),
    path('admin/recalculerAdresses/', views_admin.recalculerAdresses,  name="recalculerAdresses"),
    path('admin/recalculerAdressesConf/', views_admin.recalculerAdressesConf,  name="recalculerAdressesConf"),
    path('admin/listeContactsMails/', views_admin.listeContactsMails,  name="listeContactsMails"),
    path('admin/traduirePO/', views_admin.traduirePO,  name="traduirePO"),

    path('ajax/annonces/', views_ajax.ajax_annonces, name='ajax_categories'),
    path('ajax/nbmessages/', views_notifications.nbDerniersMessages, name='nbDerniersMessages'),
    path('ajax/ajax_salonsParTag/<str:tag>', views_ajax.salonsParTag, name='ajax_salonsParTag'),
    path('HA/api/', apiHA_pcat.initAPI, name='apiha_pcat'),

]
@login_required
def protected_serve(request, path, document_root=None, show_indexes=False):
    return serve(request, path, document_root, show_indexes)

urlpatterns += [re_path(r'^%s(?P<path>.*)$'%MEDIA_URL[1:], protected_serve,{'document_root': MEDIA_ROOT}), ]
urlpatterns += [
    re_path(r'^robots\.txt$', TemplateView.as_view(template_name="bourseLibre/robots.txt", content_type='text/plain')),
]
urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)

from django.views.generic.base import RedirectView
urlpatterns += [
    re_path(r'^favicon\.ico$', RedirectView.as_view(url='favicon.ico', permanent=True)),
    re_path(r'^browserconfig\.xml$', RedirectView.as_view(url='browserconfig.xml', permanent=True)),
    re_path(r'^android-chrome-256x256\.png$', RedirectView.as_view(url='/android-chrome-256x256.png', permanent=True)),
]
from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'annonces', views_ajax.AnnoncesViewSet)
#router.register(r'articles', views_ajax.AnnoncesViewSet)
urlpatterns += [
    path('api/', include(router.urls)),
    path('api_annonces/', include('rest_framework.urls', namespace='rest_framework')),
]

handler404 = views_base.handler404
handler500 = views_base.handler500
handler400 = views_base.handler400
handler403 = views_base.handler403

#if LOCALL:
#    import debug_toolbar
#    urlpatterns = [re_path(r'^__debug__/', include(debug_toolbar.urls)),] + urlpatterns
    #urlpatterns += re_path('',(r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}))

