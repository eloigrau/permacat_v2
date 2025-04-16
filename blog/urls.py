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

app_name = 'blog'

urlpatterns = [
    path('accueil/', views.accueil, name="acceuil"),
    path('articles/', login_required(views.ListeArticles.as_view(), login_url='/auth/login/'), name="index"),
    path(r'articles/<str:asso>', login_required(views.ListeArticles_asso.as_view(), login_url='/auth/login/'), name="index_asso"),
    # re_path(r'^newPost/', views.ajouterArticle, name='ajouterArticle'),
    # re_path(r'^article/(?P<slug>.+)$', views.lire, name='lire'),
    re_path(r'^article-ac/$', views.ArticleAutocomplete.as_view(), name='article-ac',),
    re_path(r'^article-ac-asso/$', views.ArticleAutocomplete_asso.as_view(), name='article-ac-asso',),
    re_path(r'^projet-ac/$', views.ProjetAutocomplete.as_view(), name='projet-ac',),

    path(r'article/<str:slug>', views.lireArticle, name='lireArticle'),
    path(r'article/<int:id>', views.lireArticle_id, name='lireArticle_id'),
    path(r'article/recherche/', views.lireArticle_recherche, name='lireArticle_recherche'),
    re_path(r'^modifierArticle/(?P<slug>[-\w]+)$', login_required(views.ModifierArticle.as_view(), login_url='/auth/login/'), name='modifierArticle'),
    re_path(r'^Article/AjouterAlbum/(?P<slug>[-\w]+)$', login_required(views.ArticleAddAlbum.as_view(), login_url='/auth/login/'), name='ajouterAlbumArticle'),
    re_path(r'^Article/SupprimerAlbum/(?P<slug>[-\w]+)$', views.articleSupprimerAlbum, name='supprimerAlbumArticle'),
    re_path(r'^suiveursArticle/(?P<slug>[-\w]+)$', views.articles_suivis, name='suiveursArticle'),
    path('suiveursArticles/', views.articles_suiveurs, name='suiveursArticles'),
    re_path(r'^suiveursProjet/(?P<slug>[-\w]+)$', views.projets_suivis, name='suiveursProjet'),
    re_path(r'^supprimerArticle/(?P<slug>[-\w]+)$', login_required(views.SupprimerArticle.as_view(), login_url='/auth/login/'), name='supprimerArticle'),
    path('ajouterArticle/', login_required(views.ajouterArticle), name='ajouterNouvelArticle'),
    path(r'archiverArticleAdmin/<str:slug>', login_required(views.archiverArticleAdmin), name='archiverArticleAdmin'),
    #path('post/', forms.ArticleFormPreview(forms.ArticleForm)),

    path('projets/', login_required(views.ListeProjets.as_view(), login_url='/auth/login/'), name="index_projets"),
    re_path(r'^projets/(?P<slug>[-\w]+)$', views.lireProjet, name='lireProjet'),
    re_path(r'^modifierProjet/(?P<slug>[-\w]+)$',
        login_required(views.ModifierProjet.as_view(), login_url='/auth/login/'), name='modifierProjet'),
    re_path(r'^supprimerProjet/(?P<slug>[-\w]+)$',
        login_required(views.SupprimerProjet.as_view(), login_url='/auth/login/'), name='supprimerProjet'),
    path('ajouterProjet/', views.ajouterNouveauProjet, name='ajouterNouveauProjet'),
    path(r'projets/ajouterFicheProjet/<str:slug>', views.ajouterFicheProjet, name='ajouterFicheProjet'),
    path(r'projets/modifier/<str:slug>',
        login_required(views.ModifierFicheProjet.as_view(), login_url='/auth/login/'), name='modifierFicheProjet'),
    path(r'projets/supprimer/<str:slug>',
        login_required(views.SupprimerFicheProjet.as_view(), login_url='/auth/login/'), name='supprimerFicheProjet'),
    path('telecharger_fichier/', views.telecharger_fichier, name='telechargerFichier'),

    re_path(r'^suivre_article/(?P<slug>[-\w]+)/$', views.suivre_article, name='suivre_article'),
    re_path(r'^suivre_projet/(?P<slug>[-\w]+)/$', views.suivre_projet, name='suivre_projet'),
    path(r'suivre_agora/<str:asso_abreviation>', views.suivre_articles, name='suivre_articles'),
    path('suivre_projets/', views.suivre_projets, name='suivre_projets'),
    path('filtrer_articles/', views.filtrer_articles, name='filtrer_articles'),

    path('modifierCommentaireArticle/<int:id>',
        login_required(views.ModifierCommentaireArticle.as_view(), login_url='/auth/login/'),
        name='modifierCommentaireArticle'),
    path('modifierCommentaireProjet/<int:id>',
        login_required(views.ModifierCommentaireProjet.as_view(), login_url='/auth/login/'),
        name='modifierCommentaireProjet'),

    path('ajouterEvenement/', views.ajouterEvenement, name='ajouterEvenement'),
    path('transfereArticlesJardin/', views.changerArticles_jardin, name='transfereArticlesJardin'),
    path(r'ajouterEvenementArticle/<str:slug_article>', views.ajouterEvenementArticle, name='ajouterEvenementArticle'),
    re_path(r'^supprimerEvenementArticle/(?P<slug_article>[-\w]+)-(?P<id_evenementArticle>[0-9]+)$',
        login_required(views.SupprimerEvenementArticle.as_view(), login_url='/auth/login/'),
        name='supprimerEvenementArticle'),
    path(r'ajouterSalonArticle/<str:slug_article>', views.ajouterSalonArticle, name='ajouterSalonArticle'),
    path(r'associerSalonArticle/<str:slug_article>', views.associerSalonArticle, name='associerSalonArticle'),
   path('ajouterAdresseArticle/<int:id_article>', views.ajouterAdresseArticle, name='ajouterAdresseArticle'),
    path('voirAdresseArticle/<int:id_adresseArticle>', views.voirAdresseArticle, name='voirAdresseArticle'),
    re_path(r'ajouterDocumentPartage/(?P<slug_article>[-\w]+)$', views.ajouterDocumentPartage, name='ajouterDocumentPartage'),
    re_path(r'supprimerDocumentPartage/(?P<slug_docpartage>[-\w]+)$', views.supprimerDocumentPartage, name='supprimerDocumentPartage'),
    re_path(r'modifierDocumentPartage/(?P<slug_docpartage>[-\w]+)$', views.modifierDocumentPartage, name='modifierDocumentPartage'),
    re_path(r'ajouterReunionArticle/(?P<slug_article>[-\w]+)$', views.ajouterReunionArticle, name='ajouterReunionArticle'),
    re_path(r'associerReunionArticle/(?P<slug_article>[-\w]+)$', views.associerReunionArticle, name='associerReunionArticle'),
    re_path(r'supprimerReunionArticle/(?P<slug_reunion>[-\w]+)$', views.supprimerReunionArticle, name='supprimerReunionArticle'),
    re_path(r'^supprimerAdresseArticle/(?P<slug_article>[-\w]+)/(?P<id_adresse>[0-9]+)$', login_required(views.SupprimerAdresseArticle.as_view(), login_url='/auth/login/'), name='supprimerAdresseArticle'),
    re_path(r'^modifierAdresseArticle/(?P<slug_article>[-\w]+)/(?P<id_adresse>[0-9]+)$', login_required(views.ModifierAdresseArticle.as_view(), login_url='/auth/login/'), name='modifierAdresseArticle'),
    path('voirCarteLieux/<int:id_article>', views.voirCarteLieux, name='voirCarteLieux'),
    path('voirCarteLieux_article/<int:id_article>', views.voirCarteLieux_article, name='voirCarteLieux_article'),

    path(r'ajouterTodoArticle/<str:slug_article>', views.ajouterTodoArticle, name='ajouterTodoArticle'),
    path(r'supprimerTodoArticle/<str:slug_article>/<str:slug_todo>',
        login_required(views.SupprimerTodoArticle.as_view(), login_url='/auth/login/'),
        name='supprimerTodoArticle'),
    path(r'modifierTodoArticle/<str:slug>',
        login_required(views.ModifierTodoArticle.as_view(), login_url='/auth/login/'),
        name='modifierTodoArticle'),
    path(r'todoArticle_toggle/<str:slug_article>/<str:slug_todo>',views.todoArticle_toggle,
        name='todoArticle_toggle'),
    path(r'todoArticleList/<str:asso>', login_required(views.ListeTodo_asso.as_view(), login_url='/auth/login/'),
        name='todoarticle_list'),
    path(r'todoArticleList/', login_required(views.ListeTodo_asso.as_view(), login_url='/auth/login/'),
        name='todoarticle_list'),
    path('ajax/load-categories/', views.ajax_categories, name='ajax_categories'),
    path('ajax/get_album_article_ajax/<str:article_slug>/', views.get_album_article_ajax, name='get_album_article_ajax'),
    path('ajax/articlesArchives/<str:asso>/', views.articlesArchives, name='articlesArchives'),
    path('ajax/articlesPartages/<str:asso>/', views.articlesPartages, name='articlesPartages'),
    path('ajax/articlesParTag/<str:asso>/<str:tag>/', views.articlesParTag, name='articlesParTag'),
    path('ajax/get_articles_pardossier/', views.get_articles_pardossier, name='get_articles_pardossier'),
    path('ajax/get_tags_articles/', views.get_tags_articles, name='get_tags_articles'),
    path('ajax/ajax_dernierscommentaires/', views.ajax_dernierscommentaires, name='ajax_dernierscommentaires'),
    path('voirTousLieux/', views.voirLieux, name='voirTousLieux'),

    path('ac/tag_autocomplete/', views.TagAutocomplete.as_view(), name='tag_autocomplete'),



    path(r'ajouterArticleLiens/<str:slug_article>', views.ajouterArticleLiens, name='ajouterArticleLiens'),
    path(r'supprimerArticleLiens/<str:slug_article>/<int:pk>',
         login_required(views.SupprimerArticleLiens.as_view(), login_url='/auth/login/'),
         name='supprimerArticleLiens'),
    path(r'modifierArticleLiens/<str:slug_article>/<int:pk>',
         login_required(views.ModifierArticleLiens.as_view(), login_url='/auth/login/'),
         name='modifierArticleLiens'),

    path(r'ajouterArticleLienProjet/<str:slug_article>', views.ajouterArticleLienProjet, name='ajouterArticleLienProjet'),
    path(r'supprimerArticleLienProjet/<str:slug_article>/<int:pk>',
         login_required(views.SupprimerArticleLienProjet.as_view(), login_url='/auth/login/'),
         name='supprimerArticleLienProjet'),
    path(r'modifierArticleLienProjet/<str:slug_article>/<int:pk>',
         login_required(views.ModifierArticleLienProjet.as_view(), login_url='/auth/login/'),
         name='modifierArticleLienProjet'),
    path(r'voir_articles_liens/<str:asso>/',
         views.voir_articles_liens,
        name='voir_articles_liens'),
    #path(r'get_article_liens_ajax/',
    #     views.get_article_liens_ajax,
     #   name='get_article_liens_ajax'),
    path(r'get_articles_asso_d3/<str:asso_abreviation>/',
         views.get_articles_asso_d3,
        name='get_articles_asso_d3'),
    path(r'voir_articles_liens_d3/<str:asso_abreviation>/',
         views.voir_articles_liens_d3,
        name='voir_articles_liens_d3'),
    path(r'voir_articles_liens_d3_network/<str:asso_abreviation>/',
         views.voir_articles_liens_d3_network,
        name='voir_articles_liens_d3_network'),
    path(r'get_articles_asso_d3_network/<str:asso_abreviation>/',
         views.get_articles_asso_d3_network,
        name='get_articles_asso_d3_network'),
    path(r'voir_articles_liens_d3_bubble/<str:asso_abreviation>/',
         views.voir_articles_liens_d3_bubble,
        name='voir_articles_liens_d3_bubble'),
    path(r'get_articles_asso_d3_bubble/<str:asso_abreviation>/',
         views.get_articles_asso_d3_bubble,
        name='get_articles_asso_d3_bubble')

]
