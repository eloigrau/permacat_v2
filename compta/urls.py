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
    path('facturation/devis/', views.DevisListView.as_view(), name='devis_list'),
    path('facturation/archives/', views.ArchivedDocumentListView.as_view(), name='archived_list'),

    # Détail
    path('facturation/document/<int:pk>/', views.DocumentDetailView.as_view(), name='document_detail'),

    # Création
    path('facturation/factures/creer/', views.create_document, {'doc_type': DocumentType.FACTURE}, name='facture_create'),
    path('facturation/devis/creer/', views.create_document, {'doc_type': DocumentType.DEVIS}, name='devis_create'),

    # Édition
    path('facturation/document/<int:pk>/editer/', views.update_document, name='document_update'),

    # Archivage & Restauration
    path('facturation/document/<int:pk>/archiver/', views.archive_document, name='document_archive'),
    path('facturation/document/<int:pk>/restaurer/', views.unarchive_document, name='document_unarchive'),

    # Conversion Devis -> Facture
    path('facturation/devis/<int:pk>/convertir/', views.convert_devis_to_facture, name='devis_convert'),
    path('facturation/doc/<int:pk>/dupliquer/', views.dupliquer_document, name='dupliquer_doc'),

    # Routes Vendeurs
    path('facturation/asso_infos/', views.AssoInfoListView.as_view(), name='asso_info_list'),
    path('facturation/asso_infos/add/', views.AssoInfoCreateView.as_view(), name='asso_info_create'),
    path('facturation/asso_infos/<int:pk>/edit/', views.AssoInfoUpdateView.as_view(), name='asso_info_update'),

    # Routes Produits
    path('facturation/products/', views.ProductListView.as_view(), name='product_list'),
    path('facturation/products/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('facturation/products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),

    path('facturation/clients/', views.ClientListView.as_view(), name='client_list'),
    path('facturation/clients/add/', views.ClientCreateView.as_view(), name='client_create'),
    path('facturation/clients/<int:pk>/edit/', views.ClientUpdateView.as_view(), name='client_update'),

    path('recus/', views.RecuListView.as_view(), name='recu_list'),
    path('recu/nouveau/', views.RecuCreateView.as_view(), name='recu_create'),
    path('recu/<int:pk>/', views.RecuDetailView.as_view(), name='recu_detail'),
    path('recu/<int:pk>/modifier/', views.RecuUpdateView.as_view(), name='recu_update'),
    path('recu/<int:pk>/supprimer/', views.RecuDeleteView.as_view(), name='recu_delete'),
    path('recu/<int:pk>/pdf/', views.telecharger_recu_pdf, name='recu_pdf'),
]
