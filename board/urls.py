from django.urls import path
from . import views

app_name = "board"

urlpatterns = [
    path('', views.liste_projets, name='liste_projets'),
    path('projet/nouveau/', views.creer_projetboard, name='creer_projet'),
    path('projet/<int:projet_id>/', views.detail_projetboard, name='detail_projet'),
    path('projet/<int:projet_id>/modifier/', views.modifier_projetboard, name='modifier_projet'),
    path('projet/<int:projet_id>/supprimer/', views.supprimer_projetboard, name='supprimer_projet'),
    path('api/deplacer-tache/', views.deplacer_tache, name='deplacer_tache'),
]