from django.urls import path
from . import views
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
]