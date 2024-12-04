# cal/urls.py

from . import views
from django.urls import path, include

app_name = 'agora'

urlpatterns = [
    path('', views.accueil, name="acceuil"),
    path('listeInscription/', views.listeInscription, name="listeInscription"),
    #re_path(r'^articles/$', login_required(views.ListeArticles.as_view(), login_url='/auth/login/'), name="index"),
    #path(r'articles/<str:asso>', login_required(views.ListeArticles_asso.as_view(), login_url='/auth/login/'), name="index_asso"),
    ]

from rest_framework import routers
router = routers.DefaultRouter()
router.register(r'inscriptions_at', views.InscriptionsViewSet)
urlpatterns += [
    path('api/', include(router.urls)),
    path('api_annonces/', include('rest_framework.urls', namespace='rest_framework')),
]