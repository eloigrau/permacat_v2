from django.urls import path
from . import views

app_name = 'compta'

urlpatterns = [
    path('', views.tableau_de_bord, name='tableau_de_bord'),
    path('projet/<int:projet_id>/', views.detail_projet, name='detail_projet'),
    path('transaction/ajouter/<int:projet_id>/', views.ajouter_transaction, name='ajouter_transaction'),
    #path('compta/projet/ajouter/', views.ajouter_projet, name='ajouter_projet'),
]