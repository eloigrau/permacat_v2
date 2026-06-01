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
        articleList = Article.objects.filter(asso__slug="public", estEpingle=False).annotate(
                latest=Greatest('date_modification', 'date_creation', 'date_dernierMessage')
            ).order_by('-latest')[:5]
    else:
        articleList = Article.objects.filter(asso=asso, estEpingle=False).annotate(
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

