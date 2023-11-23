# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.http import HttpResponseForbidden
from django.utils.html import strip_tags
from django.urls import reverse_lazy
from .models import Article, Commentaire, Discussion, Projet, CommentaireProjet, Choix, \
    Evenement, Asso, AdresseArticle, FicheProjet, DocumentPartage, AssociationSalonArticle
from .forms import ArticleForm, ArticleAddAlbum, CommentaireArticleForm, CommentaireArticleChangeForm, ArticleChangeForm, ProjetForm, \
    ProjetChangeForm, CommentProjetForm, CommentaireProjetChangeForm, EvenementForm, EvenementArticleForm, AdresseArticleForm,\
    DiscussionForm, SalonArticleForm, FicheProjetForm, FicheProjetChangeForm, DocumentPartageArticleForm, ReunionArticleForm,\
    AssocierReunionArticleForm, AssociationSalonArticleForm
from .filters import ArticleFilter
from.utils import get_suivis_forum
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DeleteView
from actstream import actions, action
from actstream.models import followers, following, action_object_stream
from django.utils.timezone import now
from bourseLibre.models import Suivis, Salon
from bourseLibre.settings import NBMAX_ARTICLES
from bourseLibre.forms import AdresseForm, AdresseForm2
from bourseLibre.constantes import Choix as Choix_global
from django.db.models.functions import Greatest, Lower
from bourseLibre.views import testIsMembreAsso, testIsMembreAsso_bool
from ateliers.models import Atelier
from photologue.models import Album
from defraiement.models import Reunion
from django.views.decorators.csrf import csrf_exempt
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from django.db.models import Q, F
from datetime import datetime, timedelta
import pytz
from django.utils.text import slugify
from bourseLibre.views_base import DeleteAccess
from photologue.models import Document
from vote.models import Suffrage
from dal import autocomplete
from taggit.models import Tag
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
import itertools

# @login_required
# def forum(request):
#     """ Afficher tous les articles de notre blog """
#     articles = Article.objects.all().order_by('-date_dernierMessage')  # Nous sélectionnons tous nos articles
#     return render(request, 'blog/forum.html', {'derniers_articles': articles })

@login_required
def accueil(request):
    assos = request.user.getListeAbreviationsAssosEtPublic()
    dateMin = (datetime.now() - timedelta(days=20)).replace(tzinfo=pytz.UTC)

    #derniers_articles = [x for x in Article.objects.filter(Q(date_creation__gt=dateMin) & Q(estArchive=False) & Q(asso__abreviation__in=assos)).order_by('-date_creation') if x.est_autorise(request.user)]
    #derniers_articles_comm = [x for x in Article.objects.filter(Q(date_modification__gt=dateMin) &Q(estArchive=False, dernierMessage__isnull=False) & Q(asso__abreviation__in=assos)).order_by('date_dernierMessage') if x.est_autorise(request.user)]
    #derniers_articles_modif = [x for x in Article.objects.filter(Q(date_modification__gt=dateMin) &Q(estArchive=False) & Q(date_modification__isnull=False) & ~Q(date_modification=F("date_creation")) & Q(asso__abreviation__in=assos)).order_by('date_modification') if x.est_autorise(request.user)]
    #derniers = sorted(set([x for x in itertools.chain(derniers_articles_comm[::-1][:8], derniers_articles_modif[::-1][:8], derniers_articles[:8], )]), key=lambda x:x.date_modification if x.date_modification else x.date_creation)[::-1]

    QObject = request.user.getQObjectsAssoArticles()
    articles = Article.objects.filter(Q(date_creation__gt=dateMin) & Q(estArchive=False) & QObject).order_by('-date_creation')

    derniers = articles.annotate(
        latest=Greatest('date_modification', 'date_creation', 'date_dernierMessage')
    ).order_by('-latest')
    #asso_list = [(x.nom, x.abreviation) for x in Asso.objects.all().order_by("id") if request.user.est_autorise(x.abreviation)] # ['public'] + [asso for asso in Choix_global.abreviationsAsso if self.request.user.est_autorise(asso)] + ['projets']
    asso_list = Choix_global.abreviationsNomsAssoEtPublic
    suivis = get_suivis_forum(request)

    suivi, created = Suivis.objects.get_or_create(nom_suivi='visite_forum_accueil')
    hit_count = HitCount.objects.get_for_object(suivi)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    #'categorie_list':categorie_list,'categorie_list_pc':categorie_list_pc,'categorie_list_rtg':categorie_list_rtg,'categorie_list_fer':categorie_list_fer,'categorie_list_gt':categorie_list_gt,'categorie_list_citealt':categorie_list_citealt,'categorie_list_viure':categorie_list_viure,'projets_list':projets_list,'ateliers_list':ateliers_list, 'categorie_list_projets':categorie_list_projets,
    return render(request, 'blog/accueil.html', {'asso_list':asso_list,'derniers_articles':derniers, 'suivis':suivis})


@login_required
def ajouterArticle(request):
    form = ArticleForm(request, request.POST or None)
    time_threshold = datetime.now() - timedelta(hours=24)
    articles = Article.objects.filter(auteur=request.user, date_creation__gt=time_threshold)
    if not request.user.is_superuser and len(articles) > NBMAX_ARTICLES:
        return render(request, 'erreur2.html', {"msg": "Vous avez déjà posté %s articles depuis 24h, veuillez patienter un peu avant de poster un nouvel article, merci !"% NBMAX_ARTICLES})

    if form.is_valid():
        article = form.save(request.user, sendMail=False)
        for asso in form.cleaned_data["partagesAsso"]:
            article.partagesAsso.add(asso)
        article.save(sendMail=True, forcerCreationMails=True)
        form.save_m2m()
        url = article.get_absolute_url() + "#ref-titre"
        suffix = "_" + article.asso.abreviation
        action.send(request.user, verb='article_nouveau'+suffix, action_object=article, url=url,
                    description="a ajouté un article : '%s'" % article.titre)
        suivre_article(request, article.slug)
        return redirect(article.get_absolute_url())

    return render(request, 'blog/ajouterArticle.html', { "form": form, })


# @login_required
class ModifierArticle(UpdateView):
    model = Article
    form_class = ArticleChangeForm
    template_name_suffix = '_modifier'

    def form_valid(self, form):
        self.object = form.save(sendMail=False, commit=False, )
        self.object.date_modification = now()
        self.object.save(sendMail=form.changed_data != ['estArchive'])
        form.save_m2m()

        url = self.object.get_absolute_url()
        suffix = "_" + self.object.asso.abreviation
        if not self.object.estArchive:
            desc = "a modifié l'article [%s]: '%s'" %(self.object.asso, self.object.titre)
            if 'description_modif' in form.changed_data:
                desc += " > " + form.cleaned_data['description_modif'] + " "
            if self.object.date_modification - self.object.date_creation > timedelta(minutes=10):
                action.send(self.request.user, verb='article_modifier'+suffix, action_object=self.object, url=url,
                             description=desc)
        elif form.changed_data == ['estArchive']:
            action.send(self.request.user, verb='article_modifier'+suffix + "-archive", action_object=self.object, url=url,
                         description="a archivé l'article [%s]: '%s'" %(self.object.asso, self.object.titre))

        #envoi_emails_articleouprojet_modifie(self.object, "L'article " +  self.object.titre + "a été modifié", True)
        return HttpResponseRedirect(self.get_success_url())

    def get_form(self,*args, **kwargs):
        form = super(ModifierArticle, self).get_form(*args, **kwargs)
        form.fields["asso"].choices = [(x.id, x.nom) for i, x in enumerate(Asso.objects.all().order_by('id')) if self.request.user.estMembre_str(x.abreviation)]
        form.fields["album"].choices = [("", "---------")] + [(x.id, x.title) for i, x in enumerate(Album.objects.all().order_by('title')) if self.request.user.estMembre_str(x.asso.abreviation)]

        return form

def archiverArticleAdmin(request, slug):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    article = get_object_or_404(Article, slug=slug)
    article.estArchive = True
    article.save(sendMail=False)
    url = article.get_absolute_url()
    suffix = "_" + article.asso.abreviation
    action.send(request.user, verb='article_modifier_archiver' + suffix, action_object=article, url=url,
                description="a archivé l'article")

    return redirect('blog:acceuil')


# @login_required
class ArticleAddAlbum(UpdateView):
    model = Article
    form_class = ArticleAddAlbum
    template_name_suffix = '_ajouteralbum'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Article.objects.get(slug=self.kwargs['slug'])

    def form_valid(self, form):
        self.object = form.save()
        self.object.date_modification = now()
        self.object.save(sendMail=False)
        if not self.object.estArchive:
            url = self.object.get_absolute_url()
            suffix = "_" + self.object.asso.abreviation
            action.send(self.request.user, verb='article_modifier'+suffix, action_object=self.object, url=url,
                         description="a associé un album à l'article: '%s'" % self.object.titre)
        #envoi_emails_articleouprojet_modifie(self.object, "L'article " +  self.object.titre + "a été modifié", True)
        return HttpResponseRedirect(self.get_success_url())

    def get_form(self,*args, **kwargs):
        form = super(ArticleAddAlbum, self).get_form(*args, **kwargs)
        form.fields["album"].choices = [("", "---------")] + [(x.id, x.title) for i, x in enumerate(Album.objects.all().order_by('title')) if self.request.user.estMembre_str(x.asso.abreviation)]

        return form

@login_required
def articleSupprimerAlbum(request, slug):
    art = Article.objects.get(slug=slug)
    if not art.estModifiable and art.auteur != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation de supprimer")
    art.album = None
    art.save()
    return redirect(art.get_absolute_url())


class SupprimerArticle(DeleteAccess, DeleteView):
    model = Article
    success_url = reverse_lazy('blog:index')
    template_name_suffix = '_supprimer'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Article.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self, *args, **kwargs):
        suffix = "_" + self.object.asso.abreviation
        action.send(self.request.user, verb='suppression_article'+suffix,
                     description="a supprimé l'article: '%s'" % self.object.titre)
        return super(SupprimerArticle, self).get_success_url(*args, **kwargs)


@login_required
def lireArticle(request, slug):
    article = get_object_or_404(Article, slug=slug)
    ateliers = Atelier.objects.filter(article=article).order_by('-start_time')
    documents = Document.objects.filter(article=article).order_by('date_creation')
    lieux = AdresseArticle.objects.filter(article=article).order_by('titre')
    salons = Salon.objects.filter(article=article).order_by('titre')
    salons_article = AssociationSalonArticle.objects.filter(article=article).order_by('salon__titre')
    salons = [s for s in salons if s.est_autorise(request.user)] + [s.salon for s in salons_article if s.salon.est_autorise(request.user)]
    suffrages = Suffrage.objects.filter(article=article).order_by('titre')
    suffrages = [s for s in suffrages if s.est_autorise(request.user)]
    documents_partages = DocumentPartage.objects.filter(article=article)
    reunions = Reunion.objects.filter(article=article)

    if not article.est_autorise(request.user):
        return render(request, 'notMembre.html', {"asso": str(article.asso)})

    discussions = article.discussion_set.all().order_by('id')
    commentaires = {discu:Commentaire.objects.filter(discussion=discu).order_by("date_creation") for discu in discussions}
    dates = Evenement.objects.filter(article=article).order_by("-start_time")

    actions = action_object_stream(article)
    #modifs = ModificationArticle.objects.filter(article=article)

    hit_count = HitCount.objects.get_for_object(article)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    form_discussion = DiscussionForm(request.POST or None, prefix="newdiscussionform")
    form = CommentaireArticleForm(request.POST or None)
    if form_discussion.is_valid() and not Discussion.objects.filter(slug=slugify(form_discussion.cleaned_data['titre']), article=article):
        if form_discussion.valider_unique(article):
            discu = form_discussion.save(commit=False)
            discu.article = article
            form_discussion.save()
            discussions = article.discussion_set.all().order_by('id')
            commentaires = {discu: Commentaire.objects.filter(discussion=discu).order_by("date_creation") for discu in
                            discussions}

            context = {'article': article, 'form': CommentaireArticleForm(None), 'form_discussion': form_discussion, 'commentaires': commentaires,
                       'dates': dates, 'actions': actions, 'ateliers': ateliers, 'lieux': lieux, 'documents':documents, "salons":salons,
                       "documents_partages":documents_partages, "reunions":reunions,"ancre": discu.slug}

    elif form.is_valid() and 'message_discu' in request.POST:
        discu = Discussion.objects.get(article=article, slug=request.POST['message_discu'].replace("#",""))
        comment = form.save(commit=False)
        form_discussion = DiscussionForm(request.POST or None, prefix="newdiscussionform")

        utc = pytz.UTC
        date_limite = utc.localize(datetime.today() - timedelta(hours=1))
        if comment and not Commentaire.objects.filter(commentaire=comment.commentaire, article=article, date_creation__gt=date_limite):
            comment.article = article
            comment.discussion = discu
            comment.auteur_comm = request.user
            article.sendMail = False
            article.date_dernierMessage = now()
            article.dernierMessage = ("(" + str(comment.auteur_comm) + ") " + str(strip_tags(comment.commentaire).replace('&nspb',' ')))[:96]
            if len(("(" + str(comment.auteur_comm) + ") " + str(strip_tags(comment.commentaire).replace('&nspb',' ')))) > 96:
                article.dernierMessage += "..."
            form.save()
            article.save(sendMail=False, saveModif=False)
            suffix = "_" + article.asso.abreviation
            if discu.slug == 'discussion-generale':
                url = article.get_absolute_url()+"#idConversation"
                desc = "a réagi à l'article: '%s'" % article.titre
                action.send(request.user, verb='article_message'+suffix, action_object=article, url=url,
                        description=desc, discussion=discu.titre)
            else:
                url = article.get_absolute_url()+"?ancre=" + discu.slug +"#idConversation"
                desc = "a réagi à l'article: (%s) '%s'" % (discu.titre, article.titre)
                action.send(request.user, verb='article_message'+suffix, action_object=article, url=url,
                            description=desc, discussion=discu.titre)

            #envoi_emails_articleouprojet_modifie(article, request.user.username + " a réagit au projet: " +  article.titre, True)
        context = {'article': article, 'form': CommentaireArticleForm(None), 'form_discussion': form_discussion, 'commentaires': commentaires,
               'dates': dates, 'actions': actions, 'ateliers': ateliers, 'lieux': lieux, 'documents':documents, "salons":salons, "ancre":discu.slug,
                   "suffrages":suffrages, "documents_partages":documents_partages, "reunions":reunions, }

    else:
        context = {'article': article, 'form': form, 'form_discussion': form_discussion, 'commentaires':commentaires, 'dates':dates, 'actions':actions, 'ateliers':ateliers,
                   'lieux':lieux, 'documents':documents, "salons":salons,"suffrages":suffrages, "documents_partages":documents_partages, "reunions":reunions,  }
    return render(request, 'blog/lireArticle.html', context,)

@login_required
def lireArticle_id(request, id):
    article = get_object_or_404(Article, id=id)
    return lireArticle(request, slug=article.slug)


class ListeArticles(ListView):
    model = Article
    context_object_name = "article_list"
    template_name = "blog/index.html"
    paginate_by = 25

    def get_queryset(self):
        self.params = dict(self.request.GET.items())
        self.q_objects = self.request.user.getQObjectsAssoArticles()
        qs = Article.objects.filter(self.q_objects).distinct()

        if "auteur" in self.params:
            qs = qs.filter(auteur__username=self.params['auteur'])
        if "categorie" in self.params:
            qs = qs.filter(categorie=self.params['categorie'])
        if "theme" in self.params:
            qs = qs.filter(themes__nom__in=[self.params['theme'], ])

        if "ordreTri" in self.params:
            if self.params['ordreTri'] == "-date_dernierMessage":
                qs = qs.filter(date_dernierMessage__isnull=False).order_by(self.params['ordreTri'])
            elif self.params['ordreTri'] == "-date_modification":
                qs = qs.filter(date_modification__isnull=False).order_by(self.params['ordreTri'])
            elif self.params['ordreTri'] == "-start_time":
                qs = qs.filter(start_time__isnull=False).order_by(self.params['ordreTri'])
            elif self.params['ordreTri'] == "titre":
                qs = qs.extra(select={'lower_name':'lower(titre)'}).order_by('lower_name')
            else:
                qs = qs.order_by(self.params['ordreTri'])
        else:
            qs = qs.annotate(
                latest=Greatest('date_modification', 'date_creation', 'date_dernierMessage')
                ).order_by('-latest')

        self.qs = qs
        return qs.filter(estArchive=False, estEpingle=False)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context['articles_epingles'] = self.qs.filter(Q(estArchive=False, estEpingle=True)).distinct()#.order_by(F('date_modification').desc(nulls_last=True), '-date_creation')
        context['articles_partages'] = []#self.qs.filter(Q(estArchive=False, partagesAsso__isnull=False))#.distinct().order_by(F('date_modification').desc(nulls_last=True), '-date_creation')
        context['articles_archives'] = self.qs.filter(Q(estArchive=True)).distinct()#.order_by(F('date_modification').desc(nulls_last=True), '-date_creation')

        context['asso_list'] = Choix_global.abreviationsNomsAssoEtPublic#[(x.nom, x.abreviation) for x in Asso.objects.all().order_by("id") if self.request.user.est_autorise(x.abreviation)]
        context['dossiers_list'] = Choix.type_annonce_base#[(x.nom, x.abreviation) for x in Asso.objects.all().order_by("id") if self.request.user.est_autorise(x.abreviation)]
        context['typeFiltre'] = "aucun"
        context['suivis'] = get_suivis_forum(self.request)
        context['ordreTriPossibles'] = Choix.ordre_tri_articles

        context['user_membreAsso'] = True
        context['asso_courante'] = ""

        if 'auteur' in self.request.GET:
            context['typeFiltre'] = "auteur"
        if 'categorie' in self.request.GET:
            context['typeFiltre'] = "categorie"
            try:
                context['categorie_courante'] = [x[1] for x in Choix.type_annonce if x[0] == self.request.GET['categorie']][0]
            except:
                try:
                    context['categorie_courante'] = [x[1] for x in Choix.type_annonce_projets if x[0] == self.request.GET['categorie']][0]
                except:
                    try:
                        projet = Projet.objects.get(slug=self.request.GET['categorie'])
                        context['categorie_courante'] = "Projet : " + projet.titre
                    except:
                        context['categorie_courante'] = "Catégorie inconnue : " + self.request.GET['categorie']

        if 'archives' in self.request.GET:
            context['typeFiltre'] = "archives"
        if 'ordreTri' in self.request.GET:
            try:
                context['ordre_triage'] = list(Choix.ordre_tri_articles.keys())[list(Choix.ordre_tri_articles.values()).index(self.request.GET['ordreTri'])]
            except:
                context['ordre_triage'] = self.request.GET['ordreTri']
        else:
            context['ordre_triage'] = "date de création"
        return context


class ListeArticles_asso(ListView):
    model = Article
    context_object_name = "article_list"
    template_name = "blog/index.html"
    paginate_by = 20

    def get_queryset(self):
        params = dict(self.request.GET.items())
        self.asso = Asso.objects.get(abreviation=self.kwargs['asso'])
        #self.q_objects = self.request.user.getQObjectsAssoArticles()
        #qs = Article.objects.filter(Q(asso__abreviation=self.asso.abreviation) & self.q_objects).distinct()
        if self.request.user.est_autorise(self.asso.abreviation):
            qs = Article.objects.filter(Q(asso__abreviation=self.asso.abreviation, estArchive=False, )).distinct()
        else:
            qs = Article.objects.filter(self.request.user.getQObjectsAssoArticles(), asso__abreviation=self.asso.abreviation, estArchive=False, )

        self.categorie = None
        if "auteur" in params:
            qs = qs.filter(auteur__username=params['auteur'])
        if "categorie" in params:
            self.categorie = params['categorie']

        if "ordreTri" in params:
            if params['ordreTri'] == "-date_dernierMessage":
                qs = qs.filter(date_dernierMessage__isnull=False)
            elif params['ordreTri'] == "-date_modification":
                qs = qs.filter(date_modification__isnull=False)
            elif params['ordreTri'] == "-start_time":
                qs = qs.filter(start_time__isnull=False)
            if params['ordreTri'] == "titre":
                qs = qs.extra(select={'lower_name':'lower(titre)'}).order_by('lower_name')
            else:
                qs = qs.order_by(params['ordreTri'])
        else:
            qs = qs.annotate(
                latest=Greatest('date_modification', 'date_creation', 'date_dernierMessage')
                ).order_by('-latest')

        self.qs = qs
        return qs.filter(Q(estEpingle=False))

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['articles_epingles'] = self.qs.filter(estEpingle=True)
        # paginator = Paginator(self.qs.filter(~Q(asso=self.asso) & Q(estArchive=False)), 20)
        # if not 'page_partages' in self.request.GET:
        #     page_number = 1
        # else:
        #     page_number = self.request.GET.get('page_partages')
        # context['page_partages_obj'] = paginator.get_page(page_number)
        #
        # paginator_archives = Paginator(self.qs.filter(Q(estArchive=True, asso=self.asso)), 20)
        # if not 'page_archives' in self.request.GET:
        #     page_number = 1
        # else:
        #     page_number = self.request.GET.get('page_archives')
        # context['page_archives_obj'] = paginator_archives.get_page(page_number)

        #context['articles_partages'] = paginator.get_page(page_number)
        # qs = self.qs
        # if self.asso.abreviation == "public":
        #     qs = qs.exclude(Q(asso__abreviation="pc")|Q(asso__abreviation="rtg")|Q(asso__abreviation="fer")|Q(asso__abreviation="gt")|Q(asso__abreviation="scic")|Q(asso__abreviation="citealt")|Q(asso__abreviation="viure")|Q(asso__abreviation="bzz2022"))
        # elif self.asso.abreviation == "projets":
        #     pass
        # else:
        #     qs = qs.filter(asso__abreviation=self.asso.abreviation)
        context['categorie_list'] = [(x[0], x[1], Choix.get_couleur(x[0])) for x in Choix.get_type_annonce_asso(self.asso.abreviation)]

        proj = Projet.objects.filter(estArchive=False)
        for nomAsso in Choix_global.abreviationsAsso:
            if not getattr(self.request.user, "adherent_" + nomAsso):
                proj = proj.exclude(asso__abreviation=nomAsso)

        context['projets_list'] = [(x.slug, x.titre, x.get_couleur) for x in proj]
        #
        # ateliers = Atelier.objects.filter(start_time__gte=now())
        # if not self.request.user.adherent_pc:
        #     ateliers = ateliers.exclude(asso__abreviation="pc")
        # if not self.request.user.adherent_fer:
        #     ateliers = ateliers.exclude(asso__abreviation="fer")
        # if not self.request.user.adherent_rtg:
        #     ateliers = ateliers.exclude(asso__abreviation="rtg")
        # context['ateliers_list'] = [(x.slug, x.titre, x.get_couleur) for x in ateliers]

        context['asso_list'] = Choix_global.abreviationsNomsAssoEtPublic#[(x.nom, x.abreviation) for x in Asso.objects.all().order_by("id") if self.request.user.est_autorise(x.abreviation)]
        context['asso_courante'] = self.asso
        context['dossier_courant'] = self.categorie
        context['user_membreAsso'] = self.request.user.est_autorise(self.asso.abreviation)
        context['asso_courante_abreviation'] = self.asso.abreviation
        context['typeFiltre'] = "aucun"
        context['suivis'] = get_suivis_forum(self.request)

        context['ordreTriPossibles'] = Choix.ordre_tri_articles

        if 'auteur' in self.request.GET:
            context['typeFiltre'] = "auteur"
        if 'categorie' in self.request.GET:
            context['typeFiltre'] = "categorie"
            context['urlCategorie'] = "&categorie=" + self.request.GET['categorie']
            try:
                context['categorie_courante'] = [x[1] for x in Choix.type_annonce if x[0] == self.request.GET['categorie']][0]
            except:
                try:
                    context['categorie_courante'] = [x[1] for x in Choix.type_annonce_projets if x[0] == self.request.GET['categorie']][0]
                except:
                    context['categorie_courante'] = ""
        else:
            context['urlCategorie'] = ""

        if 'archives' in self.request.GET:
            context['typeFiltre'] = "archives"
        if 'ordreTri' in self.request.GET:
            context['urlOrdreTri'] = "&ordreTri=" + self.request.GET['ordreTri']
            context['ordre_triage'] = list(Choix.ordre_tri_articles.keys())[list(Choix.ordre_tri_articles.values()).index(self.request.GET['ordreTri'])]
        else:
            context['urlOrdreTri'] = ""
            context['ordre_triage'] = "date de dernière modification"

        return context



@login_required
def articlesPartages(request, asso):
    asso = testIsMembreAsso_bool(request, asso)
    if not asso:
        return render(request, 'blog/ajax/listeArticles_template.html', {'article_list': [], 'asso': asso})
    q_object = Q(partagesAsso__abreviation=asso.abreviation) | Q(partagesAsso__abreviation='public')& ~Q(asso=asso) & Q(estArchive=False)
    article_list = Article.objects.filter(q_object)
    return render(request, 'blog/ajax/listeArticles_template.html', {'article_list': article_list, 'asso':asso})


@login_required
def articlesArchives(request, asso):
    asso = testIsMembreAsso_bool(request, asso)
    if not asso:
        return render(request, 'blog/ajax/listeArticles_template.html', {'article_list': [], 'asso':asso})
    article_list = Article.objects.filter(asso=asso, estArchive=True)
    return render(request, 'blog/ajax/listeArticles_template.html', {'article_list': article_list, 'asso':asso})

@login_required
def articlesParTag(request, asso, tag):
    asso = testIsMembreAsso_bool(request, asso)
    if not asso:
        return render(request, 'blog/ajax/listeArticles_template.html', {'article_list': [], 'asso':asso})
    q_objects = Q(asso__abreviation=asso.abreviation) | Q(partagesAsso__abreviation=asso.abreviation)| Q(asso__abreviation='public')| Q(partagesAsso__abreviation='public')
    article_list = Article.objects.filter(q_objects & Q(tags__name__in=[tag, ])).distinct()
    return render(request, 'blog/ajax/listeArticles_template.html', {'article_list': article_list, 'tag':tag})

@login_required
def get_articles_pardossier(request):
    q_objects = Q()
    if "asso" in request.GET:
        asso = testIsMembreAsso_bool(request, request.GET['asso'])
        if not asso:
            return render(request, 'blog/ajax/listeArticles_template.html', {'article_list': [], 'categorie_courante':request.GET['categorie']})

        q_objects = Q(asso=asso) & request.user.getQObjectsAssoArticles()

    if "categorie" in request.GET:
        q_objects = q_objects & Q(estArchive=False, categorie=request.GET['categorie'])
    else:
        q_objects = q_objects & Q(estArchive=False)

    article_list = Article.objects.filter(q_objects).distinct()
    return render(request, 'blog/ajax/listeArticles_template.html', {'article_list': article_list, 'categorie_courante':request.GET['categorie']})

@login_required
def get_tags_articles(request):
    tags = []
    if "asso" in request.GET:
        asso = testIsMembreAsso_bool(request, request.GET['asso'])
        if asso:
            q_objects = Q(asso=asso) | Q(partagesAsso__abreviation=asso.abreviation) | Q(partagesAsso__abreviation="public")
            inner_qs = set(list(Article.objects.filter(q_objects & Q(estArchive=False)).values_list('tags', flat=True).order_by('tags__name').distinct()))
        else:
            inner_qs = []
    else:
        inner_qs = set(list(Article.objects.filter(estArchive=False).values_list('tags', flat=True).distinct()))

    inner_qs.remove(None)
    if inner_qs:
        tags = [(reverse('blog:articlesParTag', kwargs={'asso':asso.abreviation, 'tag':t}), t)
                for t in Tag.objects.filter(id__in=inner_qs)]
    return render(request, 'blog/ajax/listeTags_template.html', {'tags': tags})


# @login_required
# def ajouterNouveauProjet(request):
#     ModelFormWithFileField
#         if form.is_valid():
#             #simple_upload(request, 'fichier_projet')
#             projet = form.save(request.user)
#             return render(request, 'blog/lireProjet.html', {'projet': projet})
#         return render(request, 'blog/ajouterProjet.html', { "form": form, })

@login_required
def ajouterNouveauProjet(request):
    if request.method == 'POST':
        form = ProjetForm(request, request.POST, request.FILES)
        if form.is_valid():
            # file is saved
            projet = form.save(request.user)
            url = projet.get_absolute_url()
            suivre_projet(request, projet.slug)

            suffix = "_" + projet.asso.abreviation
            action.send(request.user, verb='projet_nouveau'+suffix, action_object=projet, url=url,
                    description="a ajouté un projet : '%s'" % projet.titre)
            return redirect(url)

    else:
        form = ProjetForm(request, request.POST or None, request.FILES or None, )
    return render(request, 'blog/ajouterProjet.html', { "form": form, })

class ModifierProjet(UpdateView):
    model = Projet
    form_class = ProjetChangeForm
    template_name_suffix = '_modifier'
    #fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Projet.objects.get(slug=self.kwargs['slug'])

    def form_valid(self, form):
        self.object = form.save()
        self.object.date_modification = now()
        self.object.save()
        if not self.object.estArchive:
            url = self.object.get_absolute_url()
            suffix = "_" + self.object.asso.abreviation
            action.send(self.request.user, verb='projet_modifier'+suffix, action_object=self.object, url=url,
                         description="a modifié le projet: '%s'" % self.object.titre)
        #envoi_emails_articleouprojet_modifie(self.object, "Le projet " +  self.object.titre + "a été modifié", False)
        return HttpResponseRedirect(self.get_success_url())

    def get_form(self,*args, **kwargs):
        form = super(ModifierProjet, self).get_form(*args, **kwargs)
        form.fields["asso"].choices = [(x.id, x.nom) for x in Asso.objects.all().order_by("id") if self.request.user.estMembre_str(x.abreviation)]
        return form

class SupprimerProjet(DeleteAccess, DeleteView):
    model = Projet
    success_url = reverse_lazy('blog:index_projets')
    template_name_suffix = '_supprimer'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return Projet.objects.get(slug=self.kwargs['slug'])

@login_required
def lireProjet(request, slug):
    projet = get_object_or_404(Projet, slug=slug)

    if not projet.est_autorise(request.user):
        return render(request, 'notMembre.html', {"asso":"Permacat"})

    commentaires = CommentaireProjet.objects.filter(projet=projet).order_by("date_creation")
    actions = action_object_stream(projet)

    form = CommentProjetForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.projet = projet
        comment.auteur_comm = request.user
        projet.date_dernierMessage = comment.date_creation
        projet.dernierMessage = ("(" + str(comment.auteur_comm) + ") " + str(strip_tags(comment.commentaire).replace('&nspb',' ')))[:96] + "..."
        projet.save(sendMail=False)
        comment.save()
        url = projet.get_absolute_url()+"#idConversation"
        suffix = "_" + projet.asso.abreviation
        action.send(request.user, verb='projet_message'+suffix, action_object=projet, url=url,
                    description="a réagit au projet: '%s'" % projet.titre)
        #envoi_emails_articleouprojet_modifie(projet, request.user.username + " a réagit au projet: " +  projet.titre, False)
        return redirect(request.path)

    return render(request, 'blog/lireProjet.html', {'projet': projet, 'form': form, 'commentaires':commentaires, 'actions':actions},)

@login_required
def ajouterFicheProjet(request, slug):
    form = FicheProjetForm(request.POST or None)
    projet = Projet.objects.get(slug=slug)
    if form.is_valid():
        # file is saved
        fiche_projet = form.save(projet)
        url = fiche_projet.get_absolute_url()

        suffix = "_" + fiche_projet.projet.asso.abreviation
        action.send(request.user, verb='projet_nouveau'+suffix + "_ficheProjet", action_object=fiche_projet.projet, url=url,
                description="a ajouté une 'fiche projet' : '%s'" % fiche_projet.projet.titre)
        return redirect(url)

    return render(request, 'blog/ficheprojet_creer.html', { "form": form, "projet":projet})

class ModifierFicheProjet(UpdateView):
    model = FicheProjet
    form_class = FicheProjetChangeForm
    template_name_suffix = '_modifier'
    #fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return FicheProjet.objects.get(projet__slug=self.kwargs['slug'])

    def form_valid(self, form):
        self.object = form.save()
        self.object.date_modification = now()
        self.object.save()
        if not self.object.projet.estArchive:
            url = self.object.get_absolute_url()
            suffix = "_" + self.object.projet.asso.abreviation
            action.send(self.request.user, verb='projet_modifier'+suffix+"ficheProjet", action_object=self.object, url=url,
                         description="a modifié la fiche du projet: '%s'" % self.object.projet.titre)
        #envoi_emails_articleouprojet_modifie(self.object, "Le projet " +  self.object.titre + "a été modifié", False)
        return HttpResponseRedirect(self.get_success_url())


class SupprimerFicheProjet(DeleteAccess, DeleteView):
    model = FicheProjet
    success_url = reverse_lazy('blog:index_projets')
    template_name_suffix = '_supprimer'
#    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    def get_object(self):
        return FicheProjet.objects.get(projet__slug=self.kwargs['slug'])

    def get_success_url(self):
        return reverse('blog:lire_projet', kwargs={'slug':self.object.projet.slug})

@login_required
def lireProjet(request, slug):
    projet = get_object_or_404(Projet, slug=slug)

    if not projet.est_autorise(request.user):
        return render(request, 'notMembre.html', {"asso":"Permacat"})

    commentaires = CommentaireProjet.objects.filter(projet=projet).order_by("date_creation")
    actions = action_object_stream(projet)

    form = CommentProjetForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.projet = projet
        comment.auteur_comm = request.user
        projet.date_dernierMessage = comment.date_creation
        projet.dernierMessage = ("(" + str(comment.auteur_comm) + ") " + str(strip_tags(comment.commentaire).replace('&nspb',' ')))[:96] + "..."
        projet.save(sendMail=False)
        comment.save()
        url = projet.get_absolute_url()+"#idConversation"
        suffix = "_" + projet.asso.abreviation
        action.send(request.user, verb='projet_message'+suffix, action_object=projet, url=url,
                    description="a réagit au projet: '%s'" % projet.titre)
        #envoi_emails_articleouprojet_modifie(projet, request.user.username + " a réagit au projet: " +  projet.titre, False)
        return redirect(request.path)

    return render(request, 'blog/lireProjet.html', {'projet': projet, 'form': form, 'commentaires':commentaires, 'actions':actions},)


class ListeProjets(ListView):
    model = Projet
    context_object_name = "projet_list"
    template_name = "blog/index_projets.html"
    paginate_by = 50

    def get_queryset(self):
        params = dict(self.request.GET.items())

        qs = Projet.objects.all()

        if not self.request.user.is_authenticated:
            qs = qs.filter(asso__abreviation="public")
        else:
            for nomAsso in Choix_global.abreviationsAsso:
                if not getattr(self.request.user, "adherent_" + nomAsso):
                    qs = qs.exclude(asso__abreviation=nomAsso)

        if "auteur" in params:
            qs = qs.filter(auteur__username=params['auteur'])
        if "categorie" in params:
            qs = qs.filter(categorie=params['categorie'])
        if "statut" in params:
            qs = qs.filter(statut=params['statut'])

        if "asso" in params:
            qs = qs.filter(asso__abreviation=params['asso'])

        if "ordreTri" in params:
            if params['ordreTri'] == "-date_dernierMessage":
                qs = qs.filter(date_dernierMessage__isnull=False)
            elif params['ordreTri'] == "-date_modification":
                qs = qs.filter(date_modification__isnull=False)
            qs = qs.order_by(params['ordreTri'])
        else:
            qs = qs.order_by('-date_creation', '-date_dernierMessage',  'categorie', 'auteur')

        self.qs = qs
        return qs.filter(estArchive=False)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        context['list_archive'] = self.qs.filter(estArchive=True)
        # context['producteur_list'] = Profil.objects.values_list('username', flat=True).distinct()
        context['auteur_list'] = Projet.objects.order_by('auteur').values_list('auteur__username', flat=True).distinct()
        cat = Projet.objects.all().order_by('categorie').values_list('categorie', flat=True).distinct()
        context['categorie_list'] = [x for x in Choix.type_projet if x[0] in cat]
        cat = Projet.objects.all().order_by('statut').values_list('statut', flat=True).distinct()
        context['statut_list'] = [x for x in Choix.statut_projet if x[0] in cat]
        context['typeFiltre'] = "aucun"
        context['asso_list'] = Asso.objects.all().order_by("id")

        context['ordreTriPossibles'] = Choix.ordre_tri_projets

        if 'auteur_id' in self.request.GET:
            context['typeFiltre'] = "auteur"
        if 'categorie' in self.request.GET:
            context['typeFiltre'] = "categorie"
            try:
                context['categorie_courante'] = [x[1] for x in Choix.type_projet if x[0] == self.request.GET['categorie']][0]
            except:
                context['categorie_courante'] = ""
        if 'statut' in self.request.GET:
            context['typeFiltre'] = "statut"
            try:
                context['statut_courant'] = [x[1] for x in Choix.statut_projet if x[0] == self.request.GET['statut']][0]
            except:
                context['statut_courant'] = ""
        if 'asso' in self.request.GET:
            context['typeFiltre'] = "asso"
            context['asso_courante'] = Asso.objects.get(abreviation=self.request.GET["asso"]).nom
        if 'archives' in self.request.GET:
            context['typeFiltre'] = "archives"
        # if 'ordreTri' in self.request.GET:
        #     context['typeFiltre'] = "ordreTri"
        #     context['ordre_triage'] = list(Choix.ordre_tri_projets.keys())[list(Choix.ordre_tri_projets.values()).index(self.request.GET['ordreTri'])]
        # else:
        #     context['ordre_tries'] = False
        #     context['ordre_triage'] = "date du dernier message"
        context['suivis'], created = Suivis.objects.get_or_create(nom_suivi="projets")
        return context


# from django.shortcuts import render
# from django.conf import settings
# from django.core.files.storage import FileSystemStorage
#
# def simple_upload(request, nomfichier):
#     if request.method == 'POST' and request.FILES[nomfichier]:
#         myfile = request.FILES[nomfichier]
#         fs = FileSystemStorage()
#         file_path = os.path.join(settings.MEDIA_ROOT, myfile.name)
#         filename = fs.save(file_path, myfile)
#         uploaded_file_url = fs.url(filename)
#         return render(request, 'simple_upload.html', {'uploaded_file_url': uploaded_file_url})
#     return render(request, 'simple_upload.html')


import os
from django.http import HttpResponse, Http404
from django.conf import settings


@login_required
def telecharger_fichier(request):
    path = request.GET['path']
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if os.path.exists(file_path):
        mess = "fichier OK"
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read())
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    else:
        mess = "Fichier introuvable"
    return render(request, 'blog/telechargement.html', {'fichier':file_path, 'message': mess})

#
# def upload(request):
#     if request.POST:
#         form = FileForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             return render_to_response('project/upload_successful.html')
#     else:
#         form = FileForm()
#     args = {}
#     args.update(csrf(request))
#     args['form'] = form
#
#     return render_to_response('project/create.html', args)


@login_required
@csrf_exempt
def suivre_projet(request, slug, actor_only=True):
    projet = get_object_or_404(Projet, slug=slug)

    if projet in following(request.user):
        actions.unfollow(request.user, projet, send_action=False)
    else:
        actions.follow(request.user, projet, actor_only=actor_only, send_action=False)
    return redirect(projet)


@login_required
@csrf_exempt
def suivre_article(request, slug, actor_only=True):
    article = get_object_or_404(Article, slug=slug)

    if article in following(request.user):
        actions.unfollow(request.user, article, send_action=False)
    else:
        actions.follow(request.user, article, actor_only=actor_only, send_action=False)
    return redirect(article)


@login_required
def projets_suivis(request, slug):
    projet = Projet.objects.get(slug=slug)
    suiveurs = followers(projet)
    return render(request, "blog/projets_suivis.html", {'suiveurs': suiveurs, "projet":projet})

@login_required
def articles_suivis(request, slug):
    article = Article.objects.get(slug=slug)
    suiveurs = followers(article)
    return render(request, 'blog/articles_suivis.html', {'suiveurs': suiveurs, "article":article, })

@login_required
def articles_suiveurs(request, asso_abreviation='punlic'):
    suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_'+ str(asso_abreviation))
    suiveurs = sorted(followers(suivi), key= lambda x: str.lower(x.username))
    return render(request, 'blog/articles_suivis.html', {'suiveurs': suiveurs, })


@login_required
@csrf_exempt
def suivre_articles(request, asso_abreviation='public', actor_only=True):
    suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_' + str(asso_abreviation))

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi, send_action=False)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only, send_action=False)
    return redirect('blog:acceuil')

@login_required
@csrf_exempt
def suivre_projets(request, actor_only=True):
    suivi, created = Suivis.objects.get_or_create(nom_suivi='projets')

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi, send_action=False)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only, send_action=False)
    return redirect('blog:index_projets')



class ModifierCommentaireArticle(UpdateView):
    model = Commentaire
    form_class = CommentaireArticleChangeForm
    template_name = 'modifierCommentaire.html'

    def get_object(self):
        return Commentaire.objects.get(id=self.kwargs['id'])

    def form_valid(self, form):
        self.object = form.save()
        if self.object.commentaire and self.object.commentaire !='<br>':
            self.object.date_modification = now()
            self.object.save()
        else:
            self.object.delete()
        return HttpResponseRedirect(self.object.article.get_absolute_url())


class ModifierCommentaireProjet(UpdateView):
    model = CommentaireProjet
    form_class = CommentaireProjetChangeForm
    template_name = 'modifierCommentaire.html'

    def get_object(self):
        return CommentaireProjet.objects.get(id=self.kwargs['id'])

    def form_valid(self, form):
        self.object = form.save()
        if self.object.commentaire and self.object.commentaire !='<br>':
            self.object.date_modification = now()
            self.object.save()
        else:
            self.object.delete()
        return HttpResponseRedirect(self.object.projet.get_absolute_url())


@login_required
def ajouterEvenement(request, date=None):
    if date:
        form = EvenementForm(request.POST or None, initial={'start_time': date})
    else:
        form = EvenementForm(request.POST or None)

    if form.is_valid():
        form.save(request)
        return redirect('cal:agenda')

    return render(request, 'blog/ajouterEvenement.html', {'form': form, })



@login_required
def ajouterEvenementArticle(request, slug_article):
    form = EvenementArticleForm(request.POST or None)

    if form.is_valid():
        ev = form.save(request, slug_article)
        return redirect(ev.article)

    return render(request, 'blog/ajouterEvenement.html', {'form': form, })

@login_required
def ajouterDocumentPartage(request, slug_article):
    form = DocumentPartageArticleForm(request.POST or None)
    article = Article.objects.get(slug=slug_article)

    if form.is_valid():
        form.save(article)
        return redirect(article)

    return render(request, 'blog/ajouterDocumentPartage.html', {'form': form, "article": article})

@login_required
def supprimerDocumentPartage(request, slug_docpartage):
    doc = DocumentPartage.objects.get(slug=slug_docpartage)
    article = doc.article
    doc.delete()
    return redirect(article.get_absolute_url())


@login_required
def ajouterReunionArticle(request, slug_article):
    form = ReunionArticleForm(request.POST or None)
    article = Article.objects.get(slug=slug_article)

    if form.is_valid():
        form.save(article)
        return redirect(article)

    return render(request, 'blog/ajouterReunionArticle.html', {'form': form, "article": article})



@login_required
def associerReunionArticle(request, slug_article):
    art = Article.objects.get(slug=slug_article)
    form = AssocierReunionArticleForm(request.POST or None)
    if form.is_valid():
        reunion = form.cleaned_data["reunion"]
        reunion.article = art
        reunion.save()
        return redirect(reunion)

    return render(request, 'blog/ajouterReunionArticle.html', {'form': form, "article": art})

@login_required
def supprimerReunionArticle(request, slug_article):
    article = Article.objects.get(slug=slug_article)
    reu = reu.article
    reu.delete()
    return redirect(article.get_absolute_url())


@login_required
def ajouterSalonArticle(request, slug_article):
    form = SalonArticleForm(request.POST or None)
    article = Article.objects.get(slug=slug_article)

    if form.is_valid():
        ev = form.save(request, article)
        return redirect(ev.article)

    return render(request, 'blog/ajouterSalon.html', {'form': form, 'article':article, })

@login_required
def associerSalonArticle(request, slug_article):
    form = AssociationSalonArticleForm(request, request.POST or None)
    article = Article.objects.get(slug=slug_article)

    if form.is_valid():
        ev = form.save(article)
        return redirect(article)

    return render(request, 'blog/associerSalon.html', {'form': form, 'article':article})

class SupprimerEvenementArticle(DeleteAccess, DeleteView):
    model = Evenement
    success_url = reverse_lazy('blog:index')
    template_name_suffix = 'article_supprimer'

    def get_object(self):
        return Evenement.objects.get(id=self.kwargs['id_evenementArticle'])

    def get_success_url(self):
        return Article.objects.get(slug=self.kwargs['slug_article']).get_absolute_url()


@login_required
def ajouterAdresseArticle(request, id_article):
    article = Article.objects.get(id=id_article)
    form = AdresseArticleForm(request.POST or None)
    form_adresse2 = AdresseForm2(request.POST or None)

    if form_adresse2.is_valid():
        adresse = form_adresse2.save()
        form.save(article, adresse)
        return redirect(article)

    return render(request, 'blog/ajouterAdresse.html', {'article':article, 'form': form, 'form_adresse2':form_adresse2 })


class SupprimerAdresseArticle(DeleteView):
    model = AdresseArticle
    success_url = reverse_lazy('blog:index')
    template_name_suffix = '_supprimer'

    def get_object(self):
        return AdresseArticle.objects.get(id=self.kwargs['id_adresse'])

    def get_success_url(self):
        return Article.objects.get(slug=self.kwargs['slug_article']).get_absolute_url()

    def delete(self, request, *args, **kwargs):
        # the Post object
        self.object = self.get_object()
        if self.object.article.estModifiable or self.object.article.auteur == request.user or request.user.is_superuser:
            success_url = self.get_success_url()
            self.object.delete()
            return HttpResponseRedirect(success_url)
        else:
            return HttpResponseForbidden("Vous n'avez pas l'autorisation de supprimer")

@login_required
def voirCarteLieux(request, id_article):
    article = Article.objects.get(id=id_article)
    lieux = article.getLieux()
    titre = "Lieux associés à l'article '" + str(article.titre) +"'"
    return render(request, 'blog/carte_lieux.html', {'titre':titre, "lieux":lieux})

@login_required
def voirCarteLieux_article(request, id_article):
    article = Article.objects.get(id=id_article)
    lieux = article.getLieux()
    titre = "Lieux associés à l'article '" + str(article.titre) +"'"
    return render(request, 'blog/carte_lieux_template.html', {"lieux":lieux})

@login_required
def voirLieux(request,):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation de voir les lieux")
    titre = "tous les lieux"
    lieux = AdresseArticle.objects.filter().order_by('titre')

    return render(request, 'blog/carte_touslieux.html', {'titre':titre, "lieux":lieux})


@login_required
def supprimerAtelierArticle(request, article_slug, atelier_slug):
    atelier = Atelier.objects.get(slug=atelier_slug)
    if atelier.auteur != request.user and not request.user.is_superuser:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation de supprimer")
    atelier.article = None
    atelier.save()

    return lireArticle(request, article_slug)

# methode pour migrer les donnees
def changerArticles_jardin(request):
    from jardinpartage.models import Article as Art_jardin, Commentaire as Comm_jardin
    articles = Article.objects.filter(categorie="Jardin")
    for article in articles:
        new_art = Art_jardin.objects.create(categorie='Discu',
                                titre = article.titre,
                                auteur = article.auteur,
                                slug = article.slug,
                                contenu = article.contenu,
                                date_creation = article.date_creation,
                                date_modification = article.date_modification,
                                estPublic = article.estPublic,
                                estModifiable = article.estModifiable,
                            
                                date_dernierMessage = article.date_dernierMessage,
                                dernierMessage = article.dernierMessage,
                                estArchive = article.estArchive,)
        commentaires = Commentaire.objects.filter(article=article)
        for commentaire in commentaires:
            new = Comm_jardin.objects.create(auteur_comm = commentaire.auteur_comm, commentaire = commentaire.commentaire,
                                     article = new_art, date_creation= commentaire.date_creation)
        article.delete()

    return render(request, 'blog/accueil.html')



@login_required
def filtrer_articles(request):
    articles_list = Article.objects.none()
    if request.GET:
        q_object = request.user.getQObjectsAssoArticles()
        articles_list = Article.objects.filter(q_object).distinct()

    f = ArticleFilter(request.GET, queryset=articles_list)

    return render(request, 'blog/article_filter.html', {'filter': f})


def ajax_categories(request):
    try:
        asso_id = request.GET.get('asso')
        nomAsso = Asso.objects.get(id=asso_id).abreviation
        if "categorie_courante" in request.GET:
            cat = request.GET["categorie_courante"]
        else:
            cat = None

        return render(request, 'blog/ajax/categories_dropdown_list_options.html',
                      {'categories': Choix.get_type_annonce_asso(nomAsso), 'categorie_courante':cat})
    except:
        return render(request, 'blog/ajax/categories_dropdown_list_options.html', {'categories': Choix.get_type_annonce_asso("defaut")})


def ajaxListeArticles(request):
    try:
        asso_id = request.GET.get('asso')
        nomAsso = Asso.objects.get(id=asso_id).abreviation
        if getattr(request.user, "adherent_" + nomAsso):
            qs = Article.objects.filter(estArchive=False, asso__abreviation=nomAsso)
        else:
            qs = Article.objects.none()
        return render(request, 'blog/ajax/listeArticles.html',
                      {'qs': qs})
    except:
        qs = Article.objects.filter(estArchive=False)
        for nomAsso in Choix_global.abreviationsAsso:
            if not getattr(request.user, "adherent_" + nomAsso):
                qs = qs.exclude(asso__abreviation=nomAsso)
        return render(request, 'blog/ajax/categories_dropdown_list_options.html', {'qs': qs})


class TagAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated():
            return Tag.objects.none()

        qs = Tag.objects.all()

        if self.q:
            qs = qs.filter(name__istartswith=self.q)

        return qs