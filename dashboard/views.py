from django.views.generic import TemplateView
from .web_project import TemplateLayout
from photologue.models import Document
from blog.models import Article, Commentaire
from bourseLibre.views import testIsMembreAsso_bool
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import datetime, timedelta
import pytz
from django.db.models import Q
from django.db.models.functions import Greatest

from blog.models import Article, Projet, Evenement
from bourseLibre.models import EvenementSalon, InscritSalon, Salon
from ateliers.models import Atelier
"""
This file is a view controller for multiple pages as a module.
Here you can override the page view layout.
Refer to dashboards/urls.py file for more pages.
"""


class DashboardView(TemplateView):
    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        self.request.session["asso_slug"] = "ssa" #self.kwargs['asso']
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))

        return context




@login_required
def derniersDocs(request, asso):
    asso = testIsMembreAsso_bool(request, asso)
    if not asso:
        docsList = Document.objects.filter(asso__slug="public").order_by("-date_creation")[:5]
    else:
        docsList = Document.objects.filter(asso=asso).order_by("-date_creation")[:5]
    return render(request, 'ajax/docList.html', {'docList': docsList, 'asso': asso})


@login_required
def derniersArticles(request, asso):
    asso = testIsMembreAsso_bool(request, asso)
    if not asso:
        articleList = Article.objects.filter(asso__slug="public", estEpingle=False, estArchive=False).annotate(
                latest=Greatest('date_modification', 'date_creation', 'date_dernierMessage')
            ).order_by('-latest')[:5]
    else:
        articleList = Article.objects.filter(asso=asso, estEpingle=False, estArchive=False).annotate(
                latest=Greatest('date_modification', 'date_creation', 'date_dernierMessage')
            ).order_by('-latest')[:5]
    return render(request, 'ajax/articleList.html', {'articleList': articleList, 'asso': asso})


@login_required
def derniersCommentaires(request, asso):
    asso = testIsMembreAsso_bool(request, asso)
    if not asso:
        return render(request, 'ajax/commList.html', {'commList': []})
    dateMin = (datetime.now() - timedelta(days=30)).replace(tzinfo=pytz.UTC)
    derniers_comm = Commentaire.objects.filter(
        Q(article__asso=asso, date_creation__gt=dateMin) & request.user.getQObjectsAssoCommentaires()).order_by('-date_creation')[:5]
    return render(request, 'ajax/commList.html', {'commList': derniers_comm})


@login_required
def prochainesDates(request, asso):
    asso = testIsMembreAsso_bool(request, asso)
    Q_filter = Q(start_time__gt=datetime.now().date())

    if not asso:
        asso = "public"

    salons_inscrit = InscritSalon.objects.filter(profil=request.user, salon__type_salon=1).order_by("salon__titre")
    salons_prives = [s.salon for s in salons_inscrit]
    salons_publics = Salon.objects.filter(type_salon=0).order_by("titre")
    salons_groupes = [s for s in Salon.objects.filter(type_salon=2).order_by("titre") if s.est_autorise(request.user)]

    events = [
        #"articles":
            Article.objects.filter((Q(asso=asso) | Q(partagesAsso=asso) | Q(partagesAsso__slug='public')) & Q_filter).order_by("start_time")[:5],
        #"projets":
        Projet.objects.filter(Q(asso=asso) & Q_filter).order_by("start_time")[:5],
        #"ateliers":
        Atelier.objects.filter(Q(asso=asso) & Q_filter).order_by("start_time")[:5],
        #"events":
        Evenement.objects.filter(Q(article__asso=asso) & Q_filter).order_by("start_time")[:5],
        #"salon":
        EvenementSalon.objects.filter((Q(salon__in=salons_prives) | Q(salon__in=salons_publics) | Q(salon__in=salons_groupes)) & Q_filter).order_by("start_time")[:5],
    ]

    return render(request, 'ajax/datesList.html', {'datesList': events, 'asso': asso})