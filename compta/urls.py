from django.urls import path
from . import views
from .models import DocumentType
from django.contrib.auth.decorators import login_required

app_name = 'compta'

urlpatterns = [
    path('', views.tableau_de_bord, name='tableau_de_bord'),
    path('budget/detail/<int:budget_id>/', views.detail_budget, name='detail_budget'),
    path('transaction/ajouter/<int:projet_id>/', views.ajouter_transaction, name='ajouter_transaction'),
    path('transaction/modifier/<int:pk>/',
         login_required(views.ModifierTransaction.as_view(), login_url='/auth/login/'), name='modifier_transaction'),
    path('transaction/supprimer/<int:pk>/',
         login_required(views.SupprimerTransaction.as_view(), login_url='/auth/login/'), name='supprimer_transaction'),
    path('budget/ajouter/', views.ajouter_budgetProjet, name='ajouter_budgetProjet'),
    #path('compta/projet/ajouter/', views.ajouter_projet, name='ajouter_projet'),

    path('facturation/acceuil/', views.acceuil, name='facturation_acceuil'),

    path('facture/<int:facture_id>/pdf/', views.generate_facture_pdf, name='facture_pdf'),

    path('factures/', views.FactureListView.as_view(), name='facture_list'),
    path('devis/', views.QuoteListView.as_view(), name='quote_list'),
    path('archives/', views.ArchivedDocumentListView.as_view(), name='archived_list'),

    # Détail
    path('document/<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),

    # Création
    path('factures/creer/', views.create_document, {'doc_type': DocumentType.INVOICE}, name='facture_create'),
    path('devis/creer/', views.create_document, {'doc_type': DocumentType.QUOTE}, name='quote_create'),

    # Édition
    path('document/<int:pk>/editer/', views.update_document, name='document_update'),

    # Archivage & Restauration
    path('document/<int:pk>/archiver/', views.archive_document, name='document_archive'),
    path('document/<int:pk>/restaurer/', views.unarchive_document, name='document_unarchive'),

    # Conversion Devis -> Facture
    path('devis/<int:pk>/convertir/', views.convert_quote_to_facture, name='quote_convert'),

    # Routes Vendeurs
    path('sellers/', views.SellerListView.as_view(), name='seller_list'),
    path('sellers/add/', views.SellerCreateView.as_view(), name='seller_create'),
    path('sellers/<int:pk>/edit/', views.SellerUpdateView.as_view(), name='seller_update'),

    # Routes Produits
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),

    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/add/', views.ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_update'),
]
