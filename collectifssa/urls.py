# cal/urls.py

from . import views
from django.urls import path, include
from django.contrib.auth.decorators import login_required

app_name = 'collectifssa'

urlpatterns = [
    path('', views.accueil, name="accueil_collectifssa"),
    path('inscriptionCLA', views.inscriptionCLA, name="inscriptionCLA"),
    path('inscriptionCovoitCLA', views.inscriptionCovoitCLA, name="inscriptionCovoitCLA"),
    path('voirMessages', views.voirMessages, name="voirMessages"),
    path('modifierComm/<int:pk>', login_required(views.CommentaireMessage_modifier.as_view(), login_url='/auth/login/'), name="modifierComm"),
]
