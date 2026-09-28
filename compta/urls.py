from django.urls import path
from . import views
from .models import DocumentType
from django.contrib.auth.decorators import login_required

app_name = 'compta'

urlpatterns = [
    path('', views.tableau_de_bord, name='acceuil'),
    path('budget/', views.tableau_de_bord, name='tableau_de_bord'),
    path('budget/detail/<int:budget_id>/', views.detail_budget, name='detail_budget'),
    path('budget/transaction/ajouter/<int:projet_id>/', views.ajouter_transaction, name='ajouter_transaction'),
    path('budget/transaction/modifier/<int:pk>/',
         login_required(views.ModifierTransaction.as_view(), login_url='/auth/login/'), name='modifier_transaction'),
    path('budget/transaction/supprimer/<int:pk>/',
         login_required(views.SupprimerTransaction.as_view(), login_url='/auth/login/'), name='supprimer_transaction'),
    path('budget/ajouter/', views.ajouter_budgetProjet, name='ajouter_budgetProjet'),
    #path('compta/projet/ajouter/', views.ajouter_projet, name='ajouter_projet'),

    path('facturation/', views.acceuil, name='facturation_acceuil'),

    path('facturation/facture/<int:facture_id>/pdf/', views.generate_facture_pdf, name='facture_pdf'),

    path('facturation/factures/', views.FactureListView.as_view(), name='facture_list'),
    path('facturation/devis/', views.QuoteListView.as_view(), name='quote_list'),
    path('facturation/archives/', views.ArchivedDocumentListView.as_view(), name='archived_list'),

    # Détail
    path('facturation/document/<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),

    # Création
    path('facturation/factures/creer/', views.create_document, {'doc_type': DocumentType.INVOICE}, name='facture_create'),
    path('facturation/devis/creer/', views.create_document, {'doc_type': DocumentType.QUOTE}, name='quote_create'),

    # Édition
    path('facturation/document/<int:pk>/editer/', views.update_document, name='document_update'),

    # Archivage & Restauration
    path('facturation/document/<int:pk>/archiver/', views.archive_document, name='document_archive'),
    path('facturation/document/<int:pk>/restaurer/', views.unarchive_document, name='document_unarchive'),

    # Conversion Devis -> Facture
    path('devis/<int:pk>/convertir/', views.convert_quote_to_facture, name='quote_convert'),

    # Routes Vendeurs
    path('facturation/sellers/', views.SellerListView.as_view(), name='seller_list'),
    path('facturation/sellers/add/', views.SellerCreateView.as_view(), name='seller_create'),
    path('facturation/sellers/<int:pk>/edit/', views.SellerUpdateView.as_view(), name='seller_update'),

    # Routes Produits
    path('facturation/products/', views.ProductListView.as_view(), name='product_list'),
    path('facturation/products/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('facturation/products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),

    path('facturation/clients/', views.ClientListView.as_view(), name='client_list'),
    path('facturation/clients/add/', views.ClientCreateView.as_view(), name='client_create'),
    path('facturation/clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_update'),
]
