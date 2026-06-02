from django.urls import path
from dashboard import views

app_name = 'dashboard'


urlpatterns = [
    path("", views.DashboardView.as_view(), name="index",),
    path("choisirCollectif/", views.choisirCollectif, name="choisirCollectif",),
    path('derniersDocs/<str:asso>/', views.derniersDocs, name='derniersDocs'),
    path('derniersArticles/<str:asso>/', views.derniersArticles, name='derniersArticles'),
    path('derniersCommentaires/<str:asso>/', views.derniersCommentaires, name='derniersCommentaires'),
    path('prochainesDates/<str:asso>/', views.prochainesDates, name='prochainesDates'),
]
