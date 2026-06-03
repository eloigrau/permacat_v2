from django.urls import path
from dashboard import views
from django.contrib.auth.decorators import login_required

app_name = 'dashboard'


urlpatterns = [
    path("", login_required(views.DashboardView.as_view(), login_url='/auth/login/'), name="index",),
    path("choisirCollectif/", login_required(views.choisirCollectif, login_url='/auth/login/'), name="choisirCollectif",),
    path('derniersDocs/<str:asso>/', login_required(views.derniersDocs, login_url='/auth/login/'), name='derniersDocs'),
    path('derniersArticles/<str:asso>/', login_required(views.derniersArticles, login_url='/auth/login/'), name='derniersArticles'),
    path('derniersCommentaires/<str:asso>/', login_required(views.derniersCommentaires, login_url='/auth/login/'), name='derniersCommentaires'),
    path('prochainesDates/<str:asso>/', login_required(views.prochainesDates, login_url='/auth/login/'), name='prochainesDates'),
]
