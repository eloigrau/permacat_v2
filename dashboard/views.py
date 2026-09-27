from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404, HttpResponseRedirect
from .web_project import TemplateLayout
from photologue.models import Document
from blog.models import Article, Commentaire
from bourseLibre.utils import testIsMembreAsso_bool
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from datetime import datetime, timedelta
import pytz
from django.shortcuts import redirect
from django.db.models import Q
from django.db.models.functions import Greatest
from django.contrib.auth.mixins import UserPassesTestMixin
from django.template.loader import select_template
from blog.models import Article, Projet, Evenement, DocumentPartage
from bourseLibre.models import EvenementSalon, InscritSalon, Salon, Asso, Choix
from ateliers.models import Atelier
from django.http import HttpResponseForbidden
from .forms import ChoisirCollectifForm
from itertools import chain
from dal import autocomplete
from dal_select2_queryset_sequence.views import Select2QuerySetSequenceView
from queryset_sequence import QuerySetSequence
from .forms import GroupeForm
from django.views.generic.edit import FormMixin


class DashboardView(UserPassesTestMixin, TemplateView):

    # Predefined function
    def get_context_data(self, **kwargs):
        # A function to init the global layout. It is defined in web_project/__init__.py file
        context = TemplateLayout.init(self, super().get_context_data(**kwargs))
        context['asso_list'] = self.request.user.getListeSlugsNomsAssoEtPublic()
        self.form = GroupeForm(self.request.POST or None)
        context['form'] = self.form
        return context

    def test_func(self):
        if self.request.GET.get("asso_slug", None):
            self.request.session["asso_slug"] = self.request.GET.get("asso_slug")

        if not self.request.session.get("asso_slug", None):
            self.request.session["asso_slug"] = "public"

        try:
            self.asso = Asso.objects.get(slug=self.request.session["asso_slug"])
        except:
            return False

        return self.asso.est_autorise(self.request.user) or self.request.user.is_superuser

    def handle_no_permission(self):
        if not self.request.session.get("asso_slug", None):
            return redirect("dashboard:choisirCollectif")

        return render(self.request, "erreur.html", {"msg": "Vous n'êtes pas autorisé-e à voir ce contenu, désolé. "})

    def get_template_names(self):
        return select_template(["dashboard_"+ self.request.session["asso_slug"] + ".html","dashboard_base.html"])

    # def post(self, request):
    #     form = self.get_form()
    #     if form.is_valid():
    #         # Récupère l'objet sélectionné (Article ou Video) sans pour autant le sauvegarder en BDD
    #         selected_object = form.cleaned_data['target_object']
    #
    #         if selected_object and hasattr(selected_object, 'get_absolute_url'):
    #             #Redirection magique vers l'URL spécifique du modèle
    #             return redirect(selected_object.get_absolute_url())
    #     return

    def post(self, request, **kwargs):
        if self.form.is_valid():
            # Récupère l'objet sélectionné  sans pour autant le sauvegarder en BDD
            selected_object = self.form.cleaned_data['target_object']

            if selected_object and hasattr(selected_object, 'get_absolute_url'):
                return redirect(selected_object.get_absolute_url())

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

@login_required
def choisirCollectif(request):
    form = ChoisirCollectifForm(request, request.POST or None)
    if form.is_valid():
        request.session["asso_slug"] = form.cleaned_data["asso"].slug
        if "next" in request.GET:
            url_new = request.GET["next"]
            for slug in Choix.slugsAssoEtPublic:
                url_new = url_new.replace(
                    "/"+slug+"/", "/"+request.session["asso_slug"] + "/").replace(
                    "asso="+slug, "asso="+request.session["asso_slug"]).replace(
                    "asso_slug="+slug, "asso_slug="+request.session["asso_slug"])
            return redirect(url_new)
        return redirect("dashboard:index")
    return render(request, "choisirCollectif.html", {"form":form})


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
    return render(request, 'ajax/articleList.html', {'articleList': articleList, 'asso': asso, "voir_derniers":True})

@login_required
def articlesEpingles(request, asso):
    asso = testIsMembreAsso_bool(request, asso)
    if not asso:
        articleList = Article.objects.filter(asso__slug="public", estEpingle=True, estArchive=False).annotate(
                latest=Greatest('date_modification', 'date_creation', 'date_dernierMessage')
            ).order_by('-latest')
    else:
        articleList = Article.objects.filter(asso=asso, estEpingle=True, estArchive=False).annotate(
                latest=Greatest('date_modification', 'date_creation', 'date_dernierMessage')
            ).order_by('-latest')
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
        Article.objects.filter(Q(asso=asso) & Q_filter).order_by("start_time")[:5],
        #"projets":
        Projet.objects.filter(Q(asso=asso) & Q_filter).order_by("start_time")[:5],
        #"ateliers":
        Atelier.objects.filter(Q(asso=asso) & Q_filter).order_by("start_time")[:5],
        #"events":
        Evenement.objects.filter(Q(article__asso=asso) & Q_filter).order_by("start_time")[:5],
        #"salon":
        EvenementSalon.objects.filter((Q(salon__in=salons_prives) | Q(salon__in=salons_publics) | Q(salon__in=salons_groupes)) & Q_filter).order_by("start_time")[:5],
    ]
    queryset = sorted(
        chain(events[0], events[1], events[2], events[3], events[4], ),
        key=lambda instance: instance.start_time,
        reverse=False
    )

    events = [
        #"articles":
        Article.objects.filter((Q(partagesAsso=asso) | Q(partagesAsso__slug='public')) & Q_filter).order_by("start_time")[:5],
        #"projets":
        Projet.objects.filter(Q(asso__slug="public") & Q_filter).order_by("start_time")[:5],
        #"ateliers":
        Atelier.objects.filter(Q(asso__slug="public") & Q_filter).order_by("start_time")[:5],
        #"events":
        Evenement.objects.filter((Q(article__asso__slug="public")) & Q_filter).order_by("start_time")[:5],
    ]
    queryset_public = sorted(
        chain(events[0], events[1], events[2], events[3], ),
        key=lambda instance: instance.start_time,
        reverse=False
    )

    return render(request, 'ajax/datesList.html', {'datesList': queryset, 'datesList_public': queryset_public, 'asso': asso})





class GroupeSearchAutocomplete(Select2QuerySetSequenceView):
    def get_queryset(self):
        # Récupération de tous les objets des modèles cibles
        calc = len(self.q) > 1

        if not self.request.user.is_authenticated or not calc:
            return QuerySetSequence(Article.objects.none(), )

        user_slugs = self.request.user.getListeSlugsAssos_nonmembre()
        if "asso_slug" in self.request.session:
            qs_art = Article.objects.filter((self.request.user.getQObjectsAssoArticles() & Q(asso__slug=self.request.session["asso_slug"])) & Q(estArchive=False) &
                    Q(titre__icontains=self.q)).order_by("titre")
            qs_doc = Document.objects.filter(Q(asso__slug=self.request.session["asso_slug"]) &
                         Q(titre__icontains=self.q)).order_by("titre")
            qs_docptg = DocumentPartage.objects.filter(Q(article__asso__slug=self.request.session["asso_slug"]) &
                         Q(nom__icontains=self.q)).order_by("-date_creation")
            qs_projet = Projet.objects.filter(Q(asso__slug=self.request.session["asso_slug"], estArchive=False)&
                      Q(titre__icontains=self.q)).order_by("titre")
        else:
            qs_art = Article.objects.exclude(asso__slug__in=user_slugs, estArchive=True).filter(Q(titre__icontains=self.q)).order_by("titre")
            qs_doc = Document.objects.exclude(asso__slug__in=user_slugs).filter(Q(titre__icontains=self.q)).order_by("titre")
            qs_docptg = DocumentPartage.objects.exclude(asso__slug__in=user_slugs).filter(Q(nom__icontains=self.q)).order_by("-date_creation")
            qs_projet = Projet.objects.exclude(asso__slug__in=user_slugs, estArchive=True).filter(Q(titre__icontains=self.q)).order_by("titre")


        # On combine les QuerySets à l'aide de QuerySetSequence
        return QuerySetSequence(qs_art, qs_doc, qs_projet, qs_docptg)


class GFKAutocompleteView(Select2QuerySetSequenceView):
    def get_queryset(self):
        calc = len(self.q) > 1

        if not self.request.user.is_authenticated or not calc:
            return QuerySetSequence(Article.objects.none(), )

        user_slugs = self.request.user.getListeSlugsAssos_nonmembre()
        if "asso_slug" in self.request.session:
            qs_art = Article.objects.filter((self.request.user.getQObjectsAssoArticles() & Q(asso__slug=self.request.session["asso_slug"])) & Q(estArchive=False) &
                    Q(titre__icontains=self.q)).order_by("titre")
            qs_doc = Document.objects.filter(Q(asso__slug=self.request.session["asso_slug"]) &
                         Q(titre__icontains=self.q)).order_by("titre")
            qs_docptg = DocumentPartage.objects.filter(Q(article__asso__slug=self.request.session["asso_slug"]) &
                         Q(nom__icontains=self.q)).order_by("-date_creation")
            qs_projet = Projet.objects.filter(Q(asso__slug=self.request.session["asso_slug"], estArchive=False)&
                      Q(titre__icontains=self.q)).order_by("titre")
        else:
            qs_art = Article.objects.exclude(asso__slug__in=user_slugs, estArchive=True).filter(Q(titre__icontains=self.q)).order_by("titre")
            qs_doc = Document.objects.exclude(asso__slug__in=user_slugs).filter(Q(titre__icontains=self.q)).order_by("titre")
            qs_docptg = DocumentPartage.objects.exclude(asso__slug__in=user_slugs).filter(Q(nom__icontains=self.q)).order_by("-date_creation")
            qs_projet = Projet.objects.exclude(asso__slug__in=user_slugs, estArchive=True).filter(Q(titre__icontains=self.q)).order_by("titre")


        # On combine les QuerySets à l'aide de QuerySetSequence
        return QuerySetSequence(qs_art, qs_doc, qs_projet, qs_docptg)

    def get_results(self, context):
        """
        Cette méthode construit la liste JSON envoyée à Select2.
        On y injecte l'URL absolue de chaque objet.
        """
        results = []
        for result in context['object_list']:
            results.append({
                'id': self.get_result_value(result),
                'text': self.get_result_label(result),
                # 🚀 On ajoute l'URL ici pour la récupérer en JavaScript
                'url': result.get_absolute_url() if hasattr(result, 'get_absolute_url') else '#'
            })
        return results