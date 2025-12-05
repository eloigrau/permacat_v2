# -*- coding: utf-8 -*-
'''
Created on 25 mai 2017

@author: tchenrezi
'''
from django.shortcuts import HttpResponseRedirect, render, redirect, get_object_or_404#, render, redirect, render_to_response,
from django.core.exceptions import PermissionDenied
from .forms import Produit_aliment_CreationForm, Produit_vegetal_CreationForm, Produit_objet_CreationForm, \
    Produit_service_CreationForm, ContactForm, AdresseForm4, AdresseForm5, ProfilCreationForm, MessageForm, MessageGeneralForm, \
    ProfilChangeForm, Produit_aliment_modifier_form, Produit_service_modifier_form, \
    Produit_objet_modifier_form, Produit_vegetal_modifier_form, ChercherConversationForm, InviterDansSalonForm, \
    MessageChangeForm, ContactMailForm, Produit_offresEtDemandes_CreationForm, Produit_offresEtDemandes_modifier_form, \
    SalonForm, Message_salonForm, ModifierSalonDesciptionForm, Profil_rechercheForm, EvenementSalonForm, FavorisForm
from bourseLibre.forms import Profil_recherche2Form
from .models import Profil, Produit, Adresse, Choix, Panier, Item, Asso, get_categorie_from_subcat, Conversation, Message, \
    MessageGeneral, getOrCreateConversation, Suivis, InscriptionNewsletter, Salon, InscritSalon, Message_salon, InvitationDansSalon,\
   Adhesion_asso, Adhesion_permacat, EvenementSalon,MessageAdmin, Favoris
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.core.mail import mail_admins, send_mail, BadHeaderError, send_mass_mail
from local_summernote.widgets import SummernoteWidget
from random import choice
from datetime import date, timedelta, datetime
from django.http import HttpResponse
from django import forms
from django.http import Http404
from django.utils import timezone
from taggit.models import Tag

from blog.models import Article, Projet, EvenementAcceuil, Evenement, AssociationSalonArticle
from ateliers.models import Atelier
from vote.models import Suffrage, Vote
#from jardinpartage.models import Article as Article_jardin
from django_minify_html.decorators import no_html_minification
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import Group, User
from django.utils import translation
from django.core.paginator import Paginator

from django.views.decorators.debug import sensitive_variables
#from django.views.decorators.debug import sensitive_post_parameters

from django.http import HttpResponseForbidden
#from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, CharField, F
from django.utils.html import strip_tags
from hitcount.models import HitCount
from hitcount.views import HitCountMixin

from actstream import actions, action
from actstream.models import Action, Follow, following, followers, actor_stream,  any_stream, user_stream, action_object_stream, model_stream, target_stream

from django.templatetags.static import static
from django.core.exceptions import ObjectDoesNotExist
from bourseLibre.constantes import Choix as Choix_global
from django.utils.timezone import now
import pytz
from dal import autocomplete
from webpush import send_user_notification
from .views_notifications import getNbNewNotifications
from bourseLibre.views_base import DeleteAccess
from itertools import chain
from .filters import ProfilCarteFilter
from django.db.models.functions import Greatest, Lower
CharField.register_lookup(Lower, "lower")
from bourseLibre.settings.production import LOCALL, SERVER_EMAIL

def getEvenementsSemaine(request):
    current_week = date.today().isocalendar()[1]
    current_year = date.today().isocalendar()[0]
    eve_passe, eve_futur, evenements,  = [], [], []

    if not request.user.is_anonymous:
        ev_art = Evenement.objects.exclude(article__asso__slug__in=request.user.getListeSlugsAssos_nonmembre()).filter(Q(start_time__week=current_week) & Q(start_time__year=current_year)).order_by('start_time')

        ev_2 = Article.objects.exclude(asso__slug__in=request.user.getListeSlugsAssos_nonmembre()).filter(Q(start_time__week=current_week) & Q(start_time__year=current_year)).order_by('start_time')


        evenements.append(ev_2)
        #ev_3 = []
        #if request.user.adherent_jp:
        #    ev_3 = Article_jardin.objects.filter(Q(start_time__week=current_week) & Q(start_time__year=current_year)).order_by('start_time')

        ev_4 = Projet.objects.exclude(asso__slug__in=request.user.getListeSlugsAssos_nonmembre()).filter(Q(start_time__week=current_week) & Q(start_time__year=current_year)).order_by('start_time')


        ev_5 = Atelier.objects.exclude(asso__slug__in=request.user.getListeSlugsAssos_nonmembre()).filter(Q(start_time__week=current_week) & Q(start_time__year=current_year)).order_by('start_time')

        utc = pytz.UTC
        y = []
        y2 = []
        for ev in list(chain(ev_art, ev_2, ev_4, ev_5)):
            try:
                if ev.start_time >= date.today():
                    y.append((ev, date(ev.start_time.year, ev.start_time.month, ev.start_time.day)))
                else:
                    y2.append((ev, date(ev.start_time.year, ev.start_time.month, ev.start_time.day)))

            except:
                pass
        eve = sorted(y, key=lambda x:x[1])
        eve2 = sorted(y2, key=lambda x:x[1])

        #evenements = [(x, y.weekday()) for x, y in eve]
        #evenements2 = [(x, y.weekday()) for x, y in eve2]

        dict_passe = {}
        dict_futur = {}
        for ev in list(chain(ev_art, ev_2, ev_4, ev_5)):
            date_ev = ev.start_time
            if date_ev < date.today():
                if not date_ev in dict_passe.keys():
                    dict_passe[date_ev] = []
                dict_passe[date_ev].append(ev)
            else:
                if not date_ev in dict_futur.keys():
                    dict_futur[date_ev] = []
                dict_futur[date_ev].append(ev)

        liste_passe = [(date, evs) for date, evs in dict_passe.items()]
        liste_futur = [(date, evs) for date, evs in dict_futur.items()]

        eve_passe = sorted(liste_passe, key=lambda x:x[0])
        eve_futur = sorted(liste_futur, key=lambda x:x[0])

    return eve_passe, eve_futur, #dict_passe, dict_futur #evenements, evenements2

def bienvenue(request):
    nums = ['01', '02', '03', '04', '07', '10', '11', '13', '15', '17', '20', '21', '23', ]
    nomImage = 'img/flo/resized0' + choice(nums)+'.png'
    nbNotif = 0
    nbExpires = 0
    utc = pytz.UTC
    yesterday = (datetime.now() - timedelta(hours=12)).replace(tzinfo=utc)
    evenements = EvenementAcceuil.objects.filter(date__gt=yesterday).order_by('date')
    evenements_passes, evenements_semaine = getEvenementsSemaine(request)
    derniers, articles, votes = [], [], []
    invit_salons = 0

    if request.user.is_authenticated:
        nbNotif = getNbNewNotifications(request)
        nbExpires = getNbProduits_expires(request)

        suffrages = Suffrage.objects.filter(start_time__lte=datetime.now(), end_time__gte=datetime.now())
        invit_salons = InvitationDansSalon.objects.filter(profil_invite=request.user).order_by("-date_creation").count()
        for vote in suffrages:
            if vote.est_autorise(request.user):
                votes.append([vote, len(Vote.objects.filter(suffrage=vote, auteur=request.user))])

        QObject = request.user.getQObjectsAssoArticles()
        dateMin = (datetime.now() - timedelta(days=20)).replace(tzinfo=pytz.UTC)
        # derniers_articles = Article.objects.filter(
        #     Q(date_creation__gt=dateMin) & Q(estArchive=False) & QObject).order_by('-id')
        # derniers_articles_comm = Article.objects.filter(
        #     Q(date_modification__gt=dateMin) & Q(estArchive=False) & Q(dernierMessage__isnull=False) & QObject).order_by('date_dernierMessage')
        # derniers_articles_modif = Article.objects.filter(
        #     Q(date_modification__gt=dateMin) & Q(estArchive=False) & Q(date_modification__isnull=False) & ~Q(
        #         date_modification=F("date_creation")) & QObject).order_by('date_modification')
        #
        # derniers = sorted(set([x for x in
        #                        itertools.chain(derniers_articles_comm[::-1][:8], derniers_articles_modif[::-1][:8],
        #                                        derniers_articles[:8], )]),
        #                   key=lambda x: x.date_modification if x.date_modification else x.date_creation)[::-1]

        articles = Article.objects.filter(Q(date_creation__gt=dateMin) & Q(estArchive=False) & QObject).distinct().order_by('-date_creation')

        derniers = articles.annotate(
            latest=Greatest('date_modification', 'date_creation', 'date_dernierMessage')
        ).order_by('-latest')
    return render(request, 'bienvenue.html', {'nomImage':nomImage, "nbNotif": nbNotif, "nbExpires":nbExpires, "evenements":evenements, "evenements_semaine":evenements_semaine,"evenements_semaine_passes":evenements_passes, "derniers_articles":derniers, 'votes':votes, 'invit_salons':invit_salons})

class MyException(Exception):
    pass

    #return render(request, 'notMembre.html', {'asso':assos } )

def testIsMembreAsso(request, asso):
    if asso == "public":
        return Asso.objects.get(nom="Public")

    assos = Asso.objects.filter(Q(nom=asso) | Q(slug=asso))
    if assos:
        assos = assos[0]

        if not assos.is_membre(request.user) and not request.user.is_superuser:
            return render(request, 'notMembre.html', {'asso':assos } )
        return assos

    return Asso.objects.get(nom="Public")


def testIsMembreAsso_bool(request, asso):
    if asso == "public":
        return Asso.objects.get(nom="Public")

    assos = Asso.objects.filter(Q(nom=asso) | Q(slug=asso))
    if assos:
        assos = assos[0]

        if not assos.is_membre(request.user) and not request.user.is_superuser:
            return None
        return assos

    return Asso.objects.get(nom="Public")



@login_required
def produit_proposer(request, type_produit):
    try:
        bgcolor = Choix.couleurs[type_produit]
    except:
        bgcolor = None

    if type_produit == 'aliment':
        type_form = Produit_aliment_CreationForm(request, request.POST or None, request.FILES or None)
    elif type_produit == 'vegetal':
        type_form = Produit_vegetal_CreationForm(request, request.POST or None, request.FILES or None)
    elif type_produit == 'service':
        type_form = Produit_service_CreationForm(request, request.POST or None, request.FILES or None)
    elif type_produit == 'objet':
        type_form = Produit_objet_CreationForm(request, request.POST or None, request.FILES or None)
    elif type_produit == 'offresEtDemandes':
        type_form = Produit_offresEtDemandes_CreationForm(request, request.POST or None, request.FILES or None)
    else:
        raise Exception('Type de produit inconnu (aliment, vegetal, service ou  objet)')

    if type_form.is_valid():
       # produit = produit_form.save(commit=False)
        produit = type_form.save(commit=False)
        produit.user = request.user
        produit.categorie = type_produit
        produit.save()
        for monnaie in type_form.cleaned_data["monnaies"]:
            produit.monnaies.add(monnaie)
        url = produit.get_absolute_url()
        suffix = "_" + produit.asso.slug
        offreOuDemande = "offre" if produit.estUneOffre else "demande"
        titre = 'ajout_offre'+suffix
        msg = "a ajouté une "+offreOuDemande+" au marché : '%s'" %(produit.nom_produit)
        action.send(request.user, verb=titre, action_object=produit, url=url,
                    description=msg)

        messages.info(request, 'Votre offre a été ajoutée au marché, merci !')
        return HttpResponseRedirect('/marche/detail/' + str(produit.id))
    return render(request, 'bourseLibre/produit_proposer.html', {"form": type_form, "bgcolor": bgcolor, "type_produit":type_produit})


class ProduitModifier(UpdateView):
    model = Produit
    template_name_suffix = '_modifier'
    fields = ['date_debut', 'date_expiration', 'nom_produit', 'description', 'monnaies', 'prix', 'souscategorie', 'estUneOffre', 'estPublic']# 'souscategorie','etat','type_prix']

    widgets = {
        'date_debut': forms.DateInput(attrs={'type': "date"}),
        'date_expiration': forms.DateInput(attrs={'type': "date"}),
        'description': SummernoteWidget(),
    }


    def get_form_class(self):
        if self.object.categorie == 'aliment':
            return Produit_aliment_modifier_form
        elif self.object.categorie == 'vegetal':
            return Produit_vegetal_modifier_form
        elif self.object.categorie == 'service':
            return Produit_service_modifier_form
        elif self.object.categorie == 'objet':
            return Produit_objet_modifier_form
        elif self.object.categorie == 'offresEtDemandes':
            return Produit_offresEtDemandes_modifier_form
        else:
            raise Exception('Type de produit inconnu (aliment, vegetal, service ou  objet) : ' + str(self.object.categorie))

    def get_queryset(self):
        return self.model.objects.select_subclasses()

    def get_form_kwargs(self):
        kwargs = super(ProduitModifier, self).get_form_kwargs()
        kwargs.update({'request': self.request})
        return kwargs

    def get_form(self, *args, **kwargs):
        form = super(ProduitModifier, self).get_form(*args, **kwargs)
        form.fields["asso"].choices = [x for i, x in enumerate(form.fields["asso"].choices) if
                                       self.request.user.estMembre_str(x[1])]

        return form

            # @login_required

class ProduitSupprimer(DeleteAccess, DeleteView):
    model = Produit
    success_url = reverse_lazy('marche')

@login_required
def proposerProduit_entree(request):
    return render(request, 'bourseLibre/produit_proposer_entree.html', {"couleurs":Choix.couleurs})


@login_required
def detailProduit(request, produit_id):
    try:
        prod = Produit.objects.get_subclass(id=produit_id)
    except ObjectDoesNotExist:
        raise Http404

    if not prod.est_autorise(request.user):
        return render(request, 'notMembre.html',{"asso":prod.asso})
    return render(request, 'bourseLibre/produit_detail.html', {'produit': prod})


def merci(request, template_name='merci.html'):
    return render(request, template_name)


@login_required
def profil_courant(request, ):
    nbExpires = getNbProduits_expires(request)
    return render(request, 'profil.html', {'user': request.user, "nbExpires":nbExpires})

@no_html_minification
@login_required
def profil(request, user_id):
    try:
        user = Profil.objects.get(id=user_id)
        distance = user.getDistance(request.user)
        return render(request, 'profil.html', {'user': user, 'distance':distance})
    except User.DoesNotExist:
            return render(request, 'profil_inconnu.html', {'userid': user_id})

@login_required
def annuaire(request, asso):
    asso = testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied
    prof = asso.getProfils()
    nb_profils = len(prof)
    prof = prof.filter(accepter_annuaire=True)
    return render(request, 'annuaire.html', {'profils':prof, "nb_profils":nb_profils, "asso":asso} )


@login_required
def listeContacts(request, asso):
    asso = testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied
    listeMails = []
    if request.user.is_superuser and asso.slug=="pc":
        listeMails.append( {"type":'user_newsletter', "profils":Profil.objects.filter(inscrit_newsletter=True), "titre":"su : Liste des inscrits à la newsletter : "})
        listeMails.append({"type":'anonym_newsletter', "profils":InscriptionNewsletter.objects.all(), "titre":"su : Liste des inscrits anonymes à la newsletter : "})
        listeMails.append({"type":'user_adherent', "profils":Profil.objects.filter(adherent_pc=True), "titre":"su : Liste des adhérents Permacat: "})

    listeMails.append({"type":'user_adherent_ajour' , "profils":asso.getProfils_cotisationAJour(), "titre":"Liste des adhérents : à jour de leur cotisation "})

    listeMails.append(
      {"type":'user_adherent', "profils":asso.getProfils(), "titre":"Liste des membres du Groupe " + asso.nom},
    )
    listeMails.append(
      {"type":'user_adherent', "profils":asso.getProfils_sympathisants(), "titre":"Liste des sympathisants " + asso.nom},
    )
    return render(request, 'asso/listeContacts.html', {"listeMails":listeMails, "asso":asso })

@login_required
def listeAdhesions(request, asso):
    asso = testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied
    if asso.slug == "pc":
        qs = Adhesion_permacat.objects.filter().order_by("-date_cotisation")
    else:
        qs = Adhesion_asso.objects.filter(asso=asso).order_by("-date_cotisation")

    return render(request, 'asso/listeAdhesions.html', {"listeAdhesions":qs, "asso":asso })

class Adhesion_asso_modifier(UpdateView):
    model = Adhesion_asso
    template_name_suffix = '_modifier'

    def get_object(self):
        self.object = Adhesion_asso.objects.get(pk=self.kwargs['pk'])

        return self.object

    #def form_valid(self, form):
    #    self.object = form.save()
    #    return HttpResponseRedirect(self.get_success_url())


class Adhesion_asso_supprimer(DeleteView):
    model = Adhesion_asso
    template_name_suffix = '_supprimer'

    def get_success_url(self):
        return self.adherent.get_absolute_url()

    def get_object(self):
        ad = Adhesion_asso.objects.get(pk=self.kwargs['pk'])
        self.adherent = ad.adherent
        return ad


@login_required
def listeContacts_admin(request):
    if request.user.is_superuser:
        listeMails = [
            {"type":'user_newsletter' ,"profils":Profil.objects.all(), "titre":"Liste des inscrits au site : "},
        {"type":'anonym_newsletter' ,"profils":InscriptionNewsletter.objects.all(), "titre":"Liste des inscrits anonymes à la newsletter : "},
          {"type":'user_adherent', "profils":Profil.objects.filter(adherent_pc=True), "titre":"Liste des adhérents Permacat: "},
          {"type":'user_adherent', "profils":Profil.objects.filter(adherent_rtg=True), "titre":"Liste des adhérents RTG: "},
          {"type":'user_adherent', "profils":Profil.objects.filter(adherent_scic=True), "titre":"Liste des adhérents PermAgora: "},
          {"type":'user_adherent', "profils":Profil.objects.filter(adherent_citealt=True), "titre":"Liste des adhérents Cite Altruiste: "},
          {"type":'user_adherent', "profils":Profil.objects.filter(adherent_viure=True), "titre":"Liste des adhérents Viure: "},
          {"type":'user_adherent', "profils":Profil.objects.filter(adherent_bzz2022=True), "titre":"Liste des adhérents Bzzz: "},
           # {"type":'user_futur_adherent', "profils":Profil.objects.filter(statut_adhesion=0), "titre":"Liste des personnes qui veulent adhérer à Permacat :"}
        ]
    else:
        listeMails = [ ]

    return render(request, 'asso/listeContacts.html', {"listeMails":listeMails})

@login_required
def listeFollowers(request, asso):
    asso=testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied
    listeArticles = []
    for art in Article.objects.filter(asso=asso):
        suiveurs = followers(art)
        if suiveurs:
            listeArticles.append({"titre": art.titre, "url": art.get_absolute_url(), "followers": suiveurs, })
    #for art in Article_jardin.objects.all():
        #suiveurs = followers(art)
        #if suiveurs:
         #   listeArticles.append({"titre": art.titre, "url": art.get_absolute_url(), "followers": suiveurs, })
    for art in Projet.objects.filter(asso=asso):
        suiveurs = followers(art)
        if suiveurs:
            listeArticles.append({"titre": art.titre, "url": art.get_absolute_url(), "followers": suiveurs, })

    return render(request, 'listeFollowers.html', {"listeArticles":listeArticles})



@login_required
def admin_asso(request, asso):
    asso=testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied
    listeFichers = []
    if asso == 'permacat':
        listeFichers = [
            {"titre": "Télécharger le bilan comptable", "url": "{{STATIC_ROOT]]/admin/coucou.txt"},
            {"titre":"Télécharger un RIB", "url":"{{STATIC_ROOT]]/admin/bilan.txt" },
            {"titre":"Télécharger les statuts et règlement intérieur", "url":"{{STATIC_ROOT]]/admin/statuts.txt" },
        ]
    return render(request, 'asso/admin_asso.html', {"listeFichers":listeFichers, "asso":asso} )

@login_required
def admin_asso_rtg(request):
    if not request.user.adherent_rtg:
        return render(request, "notRTG.html")

    listeFichers = [
    ]
    return render(request, 'asso/admin_asso_rtg.html', {"listeFichers":listeFichers} )


def presentation_asso(request, asso):
    request.session["asso_slug"] = asso
    return render(request, 'asso/'+ asso + "/presentation_asso.html")

def organisation_citealt(request):
    return render(request, "asso/citealt/organisation.html")

def organisation_viure(request):
    return render(request, "asso/viure/organisation.html")

def presentation_groupes(request):
    return render(request, 'asso/presentation_groupes.html')

@login_required
def telechargements_asso(request, asso):
    asso=testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied
    fichiers=[]
    if asso.slug == "pc":
        fichiers = [{'titre' : 'Contrat credit mutuel', 'url': static('doc/contrat_credit_mutuel.pdf'),},
                    {'titre' : 'Procès verbal de constitution', 'url': static('doc/PV_constitution.pdf'),},
                    {'titre' : "Recepissé de création de l'asso", 'url': static('doc/recepisse_creation.pdf'),},
                    {'titre' : "Publication au journal officiel", 'url': static('doc/JOAFE_PDF_Unitaire_20190012_01238.pdf'),},
                    {'titre' : 'Statuts déposés', 'url': static('doc/statuts.pdf'),},
                    {'titre' : 'RIB', 'url': static('doc/rib.pdf'),},
                    {'titre' : 'CR AGO 2021', 'url': static('doc/CR/2021_AGO-Compte_rendu.pdf'),},
                    {'titre' : 'CR Réunion écovillage 16/04/2021', 'url': static('doc/CR/CR16AVRIL21_ecovillage.docx'),},
                    ]
    elif asso.slug == "scic":
        fichiers = [
                {'titre' : 'Fiche Projet', 'url': static('permagora/docs_admin/Fiche_Projet.pdf'),},
                {'titre' : 'Statuts-Ri-Charte', 'url': static('permagora/docs_admin/Statuts-Ri-Charte-PermAgora_final.pdf'),},
                {'titre' : 'Statuts signés', 'url': static('permagora/docs_admin/statuts_PermAgora_signes.pdf'),},
                {'titre' : 'PV création', 'url': static('permagora/docs_admin/PV_creation_permagora.pdf'),},
                {'titre' : 'Publication journal officiel', 'url': 'https://www.journal-officiel.gouv.fr/pages/associations-detail-annonce/?q.id=id:202200171115',},
                ]

    return render(request, 'asso/fichiers.html', {'fichiers':fichiers, "asso":asso})


def adhesion_entree(request):
    return render(request, 'asso/adhesion.html', )


def adhesion_asso(request, asso):
    asso = get_object_or_404(Asso, Q(nom=asso) | Q(slug=asso))
    if not asso:
        return render(request, 'asso/pc/adhesion.html', )

    return render(request, 'asso/' + asso.slug +'/adhesion.html', )


def fairedon_asso(request, asso):
    if asso == 'developpeur':
        return render(request, 'asso/fairedondeveloppeur.html', )

    asso = Asso.objects.get(Q(nom=asso) | Q(slug=asso))

    return render(request, 'asso/'+ asso.slug +'/fairedon.html', )

@login_required
def carte(request, asso):
    asso = testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied
    request.session["asso_slug"] = asso.slug
    profils = asso.getProfils()
    nbProf = len(profils)
    nb_par_page = 100
    #profils = asso.getProfils_Annuaire()
    if "lettre" in request.GET:
        profils = profils.filter(username__istartswith=request.GET["lettre"])
        nb_par_page = nbProf
    profils_filtres = ProfilCarteFilter(request.GET, queryset=profils)
    #profils_filtres = profils
    paginator = Paginator(profils_filtres.qs, nb_par_page) # Show 10 contacts per page.
    if not 'page' in request.GET:
        page_number = 1
    else:
        page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if asso.slug != "public":
        titre = "Carte/annuaire des membres du groupe %s"%(asso.nom,)
    else:
        titre = "Carte/annuaire des inscrits du site"

    # try:
    #     import simplejson
    #     import requests
    #     url = "https://presdecheznous.gogocarto.fr/api/elements.json?limit=500&bounds=1.75232%2C42.31794%2C3.24646%2C42.94034"
    #
    #     reponse = requests.get(url)
    #     data = simplejson.loads(reponse.text)
    #     ev = data["data"]
    # except:
    #     ev = []
    ev = []

    return render(request, 'carte_cooperateurs.html', {'filter':profils_filtres, 'page_obj':page_obj,'titre': titre, 'data':ev, "asso":asso} )


# @login_required
# def carte(request, asso):
#     asso = testIsMembreAsso(request, asso)
#     if not isinstance(asso, Asso):
#         raise PermissionDenied
#     profils = asso.getProfilsAnnuaire().filter(accepter_annuaire=True).order_by("username")
#     return render(request, 'carte_cooperateurs.html', {'profils':profils, 'titre': "Carte des adhérents "+str(asso) + "*" } )

@login_required
def profil_contact(request, user_id):
    recepteur = Profil.objects.get(id=user_id)
    if request.method == 'POST':
        form = ContactForm(request.POST or None, )
        if form.is_valid():
            sujet = "[permacat] "+ request.user.username + "(" + request.user.email+ ") vous a écrit: "+ form.cleaned_data['sujet']
            message_txt = ""
            message_html = form.cleaned_data['msg']
            recepteurs = [recepteur.email,]
            #if form.cleaned_data['renvoi'] :
            #    recepteurs = [recepteur.email, request.user.email]

            send_mail(
                sujet,
                message_txt,
                request.user.email,
                recepteurs,
                html_message=message_html,
                fail_silently=False,
                )
            destinataire = recepteur.username
            if recepteur.accepter_annuaire:
                destinataire += " (" +recepteur.email+ ")"

            context = {'sujet': form.cleaned_data['sujet'],
                       'msg':message_html,
                       'envoyeur':request.user.username + " (" + request.user.email + ")",
                       "destinataire":destinataire
                       }
            return render(request, 'contact/message_envoye.html', context)
    else:
        form = ContactForm()
    return render(request, 'contact/profil_contact.html', {'form': form, 'recepteur':recepteur})

    #message = None
    #titre = None
    # id_panier = request.GET.get('panier')
    # if id_panier:
    #     panier = Panier.objects.get(id=id_panier)
    #     message = panier.get_message_demande(int(user_id))
    #     titre = "Proposition d'échange"
    #
    # id_produit = request.GET.get('produit')
    # if id_produit:
    #     produit = Produit.objects.get(id=id_produit)
    #     message = produit.get_message_demande()
    #     titre = "Au sujet de l'offre de " + produit.nom_produit


def contact_admins(request):
    if request.user.is_anonymous:
        form = ContactMailForm(request.POST or None, )
    else:
        form = ContactForm(request.POST or None, )

    if form.is_valid():

        if request.user.is_anonymous:
            envoyeur = "Anonyme : " + form.cleaned_data['email']
            email = form.cleaned_data['email']
        else:
            envoyeur = request.user.username + " (" + request.user.email + ") "
            email = request.user.email
        sujet = form.cleaned_data['sujet']
        message_txt = envoyeur + " a envoyé le message suivant : "+ form.cleaned_data['msg']
        message_html = envoyeur + " a envoyé le message suivant : " + form.cleaned_data['msg']
        MessageAdmin.objects.create(email=email, message=message_txt, sujet=sujet)

        admin = Profil.objects.get(username="Eloi")
        if request.user.is_anonymous:
            action.send(admin, verb='envoi_salon_prive',  url="/gestion/bourseLibre/messageadmin/",
                description="a envoyé un message aux admin (%s)" %admin.username)
        else:
            action.send(request.user, verb='envoi_salon_prive',  url="/gestion/bourseLibre/messageadmin/",
                description="a envoyé un message aux admin (%s)" %admin.username)

        # try:
        #     envoiMailAdmin = False
        #     if envoiMailAdmin and not LOCALL:
        #         mail_admins(sujet, message_txt, html_message=message_html)
        #         if form.cleaned_data['renvoi']:
        #             if request.user.is_anonymous:
        #                 send_mail(sujet, "Vous avez envoyé aux administrateurs du site www.perma.cat le message suivant : " + message_html, form.cleaned_data['email'], [form.cleaned_data['email'],], fail_silently=False, html_message=message_html)
        #             else:
        #                 send_mail(sujet, "Vous avez envoyé aux administrateurs du site www.perma.cat le message suivant : " + message_html, request.user.email, [request.user.email,], fail_silently=False, html_message=message_html)
        #
        #     return render(request, 'contact/message_envoye.html', {'sujet': sujet, 'msg': message_html,
        #                                            'envoyeur': envoyeur ,
        #                                            "destinataire": "administrateurs "})
        # except BadHeaderError:
        #     return render(request, 'erreur.html', {'msg':'Invalid header found.'})

        #return render(request, 'erreur.html', {'msg':"Désolé, une ereur s'est produite"})

        return render(request, 'contact/message_envoye.html', {'sujet': sujet, 'msg': message_html,  'envoyeur': envoyeur ,
                                                   "destinataire": "administrateurs "})
    return render(request, 'contact/contact.html', {'form': form, "isContactProducteur":False})


@login_required
def signaler_bug(request):
    form = ContactForm(request.POST or None, )

    if form.is_valid():
        sujet = form.cleaned_data['sujet']
        message_txt = "<a href='"+request.user.get_profil_url()+"'>" + str(request.user.username) + "</a> a signalé un bug : "+ form.cleaned_data['msg']
        MessageAdmin.objects.create(email=request.user.email, message=message_txt, sujet=sujet)

        admin = Profil.objects.get(username="Eloi")
        action.send(request.user, verb='envoi_salon_prive',  url="/gestion/bourseLibre/messageadmin/",
            description="a envoyé un message aux admin (%s)" %admin.username)
        return render(request, 'contact/message_envoye.html', {'sujet': sujet, 'msg': message_txt,
                                                               "envoyeur": request.user.username,
                                                   "destinataire": "administrateurs "})

    return render(request, 'contact/signaler_bug.html', {'form': form, "isContactProducteur":False})




def contact_admins2(request):
    form = ContactForm(request.POST or None)
    if form.is_valid():
        if request.user.is_anonymous:
            envoyeur = "Anonyme"
        else:
            envoyeur = request.user.username + "(" + request.user.email + ") "
        sujet = form.cleaned_data['sujet']
        message = request.user.username + ' a envoyé le message suivant : \\n' + form.cleaned_data['message']
        mail_admins(sujet, message)
        if form.cleaned_data['renvoi'] :
            mess = "[Permacat] message envoyé aux administrateurs : \\n"
            send_mail( sujet, mess + message, request.user.email, [request.user.email,], fail_silently=False,)
        return render(request, 'contact/message_envoye.html', {'sujet': sujet, 'message':message, 'envoyeur':request.user.username + "(" + request.uer.email + ")", "destinataire":"administrateurs d"
                                                                                                                                                                       "u site)"})
    return render(request, 'contact/contact.html', {'form': form, "isContactProducteur":False})


@login_required
def produitContacterProducteur(request, produit_id):
    prod = Produit.objects.get_subclass(pk=produit_id)
    receveur = prod.user
    form = ContactForm(request.POST or None)
    if form.is_valid():
        sujet = "[Permacat] " + request.user.username + "(" + request.user.email+ ") vous contacte au sujet de: "  + form.cleaned_data['sujet']
        message = form.cleaned_data['message'] + '(par : ' + request.username + ')'

        send_mail( sujet, message, request.user.email, receveur.email, fail_silently=False,)
        if form.cleaned_data['renvoi'] :
            mess = "[Permacat] message envoyé à : "+receveur.email+"\\n"
            send_mail( sujet,mess + message, request.user.email, [request.user.email,], fail_silently=False,)

    return render(request, 'contact/contact.html', {'form': form, "isContactProducteur":True, "producteur":receveur.user.username})


@login_required
class profil_modifier_user(UpdateView):
    model = Profil
    form_class = ProfilChangeForm
    template_name_suffix = '_modifier'
    fields = ['username', 'first_name', 'last_name', 'email', 'site_web', 'description', 'competences', 'pseudo_june', 'accepter_annuaire', 'inscrit_newsletter']

    def get_object(self):
        return Profil.objects.get(id=self.request.user.id)


    def post(self, request, **kwargs):
        self.object = self.get_object()
        self.object.save(recalc=True)
        return super(profil_modifier_user, self).post(request, **kwargs)



@login_required
def modifier_adresse(request, adresse_pk):
    adresse = get_object_or_404(Adresse, pk=adresse_pk)
    form_adresse = AdresseForm5(request.POST or None, instance=adresse)

    if form_adresse.is_valid():
        adresse = form_adresse.save()
        if not hasattr(adresse, 'profil'):
            request.user.adresse=adresse
            request.user.save()
        return redirect(request.user)

    return render(request, 'registration/modifierAdresse.html', {'form_adresse':form_adresse, 'adresse':adresse })

@login_required
def profil_modifier_adresse(request):
    if not request.user.adresse:
         request.user.adresse = Adresse.objects.create(commune="Perpignan", code_postal='66000')
         request.user.save()
    form_adresse = AdresseForm5(request.POST or None, instance=request.user.adresse)

    if form_adresse.is_valid():
        adresse = form_adresse.save()
        return redirect(request.user)

    return render(request, 'registration/profil_modifierAdresse.html', {'form_adresse':form_adresse, 'adresse':request.user.adresse })

@login_required
def supprimer_adresse(request, adresse_pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    adresse = get_object_or_404(Adresse, pk=adresse_pk)
    m = str(adresse)
    try:
        adresse.delete()
    except Exception as e:
        message = "Erreur "+str(e)
        return render(request, 'message_admin.html', {'message': message,})

    message = "Adresse supprimée " + m
    return render(request, 'message_admin.html', {'message': message,})



@login_required
def profil_modifier_adresse_user(request, user_pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    profil = Profil.objects.get(pk=user_pk)
    form_adresse = AdresseForm5(request.POST or None, instance=profil)

    if form_adresse.is_valid():
        adresse = form_adresse.save()
        return redirect(profil)

    return render(request, 'registration/profil_modifierAdresse.html', {'form_adresse':form_adresse, 'adresse':request.user.adresse })

class profil_modifier(UpdateView):
    model = Profil
    form_class = ProfilChangeForm
    template_name_suffix = '_modifier'
    #fields = ['username','email','first_name','last_name', 'site_web','description', 'competences', 'inscrit_newsletter']

    def get_object(self):
        return Profil.objects.get(id=self.request.user.id)

class profil_supprimer(DeleteAccess, DeleteView):
    model = Profil
    success_url = reverse_lazy('bienvenue')

    def get_object(self):
        return Profil.objects.get(id=self.request.user.id)

@sensitive_variables('password')
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('change_password')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/password_changer_form.html', {
        'form': form
    })

@sensitive_variables('user', 'password1', 'password2')
def register(request):
    if request.user.is_authenticated:
        return redirect('bienvenue')
        return render(request, "erreur.html", {"msg":"Vous êtes déjà inscrit.e et authentifié.e !"})
    
    form_adresse = AdresseForm5(request.POST or None)
    form_profil = ProfilCreationForm(request.POST or None)
    if form_adresse.is_valid() and form_profil.is_valid():
        adresse = form_adresse.save()
        profil_courant = form_profil.save(commit=False,is_active = False)
        profil_courant.adresse = adresse
        #if profil_courant.statut_adhesion == 2:
        #    profil_courant.is_active=False
        profil_courant.save()
        #Panier.objects.create(user=profil_courant)
        return render(request, 'userenattente.html', {'pseudo':profil_courant.username})

    return render(request, 'register.html', {"form_adresse": form_adresse,"form_profil": form_profil,})


class ListeProduit(ListView):
    model = Produit
    context_object_name = "produits_list"
    template_name = "produit_list.html"
    paginate_by = 32

    def get_qs(self):
        qs = Produit.objects.select_subclasses().exclude(asso__slug__in=self.request.user.getListeSlugsAssos_nonmembre())
        if not self.request.user.is_authenticated:
            qs = qs.filter(asso__slug="public")

        params = dict(self.request.GET.items())

        if not "expire" in params:
            qs = qs.filter(Q(date_expiration__gt=date.today())| Q(date_expiration=None) )
        else:
            qs = qs.filter(Q(date_expiration__lt=date.today()) )

        
        if "distance" in params:
            listProducteurs = [p for p in Profil.objects.all() if p.getDistance(self.request.user) < float(params['distance'])] 
            qs = qs.filter(user__in=listProducteurs)

        if "producteur" in params:
            qs = qs.filter(user__username=params['producteur'])
        if "categorie" in params:
            if params['categorie'] == "liste":
                qs = qs.filter(categorie=params['categorie'])
            else:
                qs = qs.filter(categorie=params['categorie'])
        if "souscategorie" in params:
            qs = qs.filter(Q(produit_aliment__souscategorie=params['souscategorie']) | Q(produit_vegetal__souscategorie=params['souscategorie']) | Q(produit_service__souscategorie=params['souscategorie'])  | Q(produit_objet__souscategorie=params['souscategorie']))

        # if "prixmax" in params:
        #     qs = qs.filter(prix__lt=params['prixmax'])
        # if "prixmin" in params:
        #     qs = qs.filter(prix__gtt=params['prixmin'])

        if "monnaie" in params:
            qs = qs.filter(monnaies__nom=params['monnaie'])
        if "gratuit" in params:
            qs = qs.filter(unite_prix='don')
        if "offre" in params:
            qs = qs.filter(estUneOffre=params['offre'])

        if "asso" in params:
            qs = qs.filter(asso__slug=params['asso'])

        res = qs.order_by('-date_creation', 'categorie', 'user')
        if "ordre" in params:
            if params['ordre'] == 'categorie':
                res = qs.order_by('categorie', '-date_creation', 'user')
            elif params['ordre'] == "producteur" :
                res = qs.order_by('user', '-date_creation', 'categorie', )
            elif params['ordre'] == "date":
                res = qs.order_by('-date_creation', 'categorie', 'user', )

        return res

    def get_queryset(self):
        return self.get_qs()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # context['producteur_list'] = Profil.objects.values_list('user__username', flat=True).distinct()
        context['monnaie_list'] = [x[1] for x in Choix.monnaies]
        context['choixPossibles'] = Choix.choix
        context['ordreTriPossibles'] = Choix.ordreTri
        context['distancePossibles'] = Choix.distances
        #context['producteur_list'] = Profil.objects.all().order_by("username")
        context['typeFiltre'] = "aucun"
        context['asso_list'] = [(x.slug, x.nom, ) for x in Asso.objects.all().order_by("id") if self.request.user.est_autorise(x.slug)]

        # context['form'] = self.form
        if 'producteur' in self.request.GET:
            context['typeFiltre'] = "producteur"
        if 'souscategorie' in self.request.GET:
            categorie = get_categorie_from_subcat(self.request.GET['souscategorie'])
            context['categorie_parent'] = categorie
            context['typeFiltre'] = "souscategorie"
            context['souscategorie'] = self.request.GET['souscategorie']
        if 'categorie' in self.request.GET:
            context['categorie_parent'] = self.request.GET['categorie']
            context['typeFiltre'] = "categorie"
        context['typeOffre'] = ''
        if "asso" in self.request.GET:
            self.request.session["asso_slug"] = self.request.GET["asso"]
            context['asso_courante'] = Asso.objects.get(slug=self.request.GET["asso"])
        else:
            context['asso_courante'] = ""

        #elif "asso_slug" in self.request.session:
        #    self.request.session["asso_slug"] = self.request.session["asso_slug"]
        #    context['asso_courante'] = Asso.objects.get(slug=self.request.session["asso_slug"] )

        context['suivi'], created = Suivis.objects.get_or_create(nom_suivi="produits")

        suivi, created = Suivis.objects.get_or_create(nom_suivi='visite_annonces')
        hit_count = HitCount.objects.get_for_object(suivi)
        hit_count_response = HitCountMixin.hit_count(self.request, hit_count)
        return context


class ListeProduit_offres(ListeProduit):
    def get_queryset(self):
        qs = self.get_qs()
        qs = qs.filter(estUneOffre=True)
        return qs

    def get_context_data(self, **kwargs):
        context = ListeProduit.get_context_data(self, **kwargs)
        context['typeOffre'] = 'Offres'
        return context

class ListeProduit_recherches(ListeProduit):
    def get_queryset(self):
        qs = self.get_qs()
        qs = qs.filter(estUneOffre=False)
        return qs

    def get_context_data(self, **kwargs):
        context = ListeProduit.get_context_data(self, **kwargs)
        context['typeOffre'] = 'Demandes'
        return context

@login_required
def ajouterAuPanier(request, produit_id, quantite):#, **kwargs):
    quantite = float(quantite)
    produit = Produit.objects.get_subclass(pk=produit_id)
    # try:
    panier = Panier.objects.get(user=request.user, etat="a")
    # except ObjectDoesNotExist:
    #     profil = Profil.objects.get(user__id = request.user.id)
    #     panier = Panier(user=profil, )
    #     panier.save()
    ##panier.add(produit, produit.unite_prix, quantite)
    return afficher_panier(request)

@login_required
def enlever_du_panier(request, item_id):
    panier = Panier.objects.get(user=request.user, etat="a")
    panier.remove_item(item_id)
    return afficher_panier(request)


@login_required
def afficher_panier(request):
    # try:
    panier = Panier.objects.get(user=request.user, etat="a")
    # panier = get_object_or_404(Panier, user__id=profil_id, etat="a")
    # except ObjectDoesNotExist:
    #     profil = Profil.objects.get(user__id = request.user.id)
    #     panier = Panier(user=profil, )
    #     panier.save()
    items = Item.objects.order_by('produit__user').filter(panier__id=panier.id)
    return render(request, 'panier.html', {'panier':panier, 'items':items})


@login_required
def afficher_requetes(request):
    items = Item.objects.filter( produit__user__id =  request.user.id)
    return render(request, 'requetes.html', {'items':items})


@login_required
def chercher(request):
    recherche = str(request.GET.get('id_recherche')).lower()
    if recherche:
        from blog.models import Commentaire, CommentaireProjet
        produits_list = Produit.objects.exclude(asso__slug__in=request.user.getListeSlugsAssos_nonmembre()).filter(Q(description__icontains=recherche) | Q(nom_produit__lower__contains=recherche), ).select_subclasses().distinct()
        articles_list = Article.objects.exclude(asso__slug__in=request.user.getListeSlugsAssos_nonmembre()).filter(request.user.getQObjectsAssoArticles(), Q(titre__lower__contains=recherche) | Q(contenu__icontains=recherche)).distinct()
        projets_list = Projet.objects.exclude(asso__slug__in=request.user.getListeSlugsAssos_nonmembre()).filter(Q(titre__lower__contains=recherche) | Q(contenu__icontains=recherche), ).distinct()
        profils_list = Profil.objects.filter(Q(username__lower__contains=recherche)  | Q(description__icontains=recherche)| Q(competences__icontains=recherche), ).distinct()
        commentaires_list = Commentaire.objects.filter(Q(commentaire__icontains=recherche) ).distinct()
        commentairesProjet_list = CommentaireProjet.objects.filter(Q(commentaire__icontains=recherche)).distinct()
        salon_list = MessageGeneral.objects.filter(Q(message__icontains=recherche) ).distinct()
    else:
        produits_list = []
        articles_list = []
        projets_list = []
        profils_list = []
        commentaires_list, commentairesProjet_list, salon_list = [],[],[]

    return render(request, 'chercher.html', {'recherche':recherche, 'articles_list':articles_list, 'produits_list':produits_list, "projets_list": projets_list, 'profils_list':profils_list,'commentaires_list': commentaires_list, 'commentairesProjet_list':commentairesProjet_list, 'salon_list':salon_list})


@login_required
def chercher_articles(request):
    recherche = str(request.GET.get('id_recherche')).lower()
    articles_list = Article.objects.none()
    if recherche:
        from taggit.models import Tag
        tags = Tag.objects.filter(slug__icontains=recherche).values_list('name', flat=True)
        articles_list = Article.objects.filter(request.user.getQObjectsAssoArticles(), Q(tags__name__in=tags) | Q(titre__lower__icontains=recherche)).distinct()

    return render(request, 'chercherForum.html', {'recherche':recherche, 'articles_list':articles_list})

@login_required
def chercher_annonces(request):
    recherche = str(request.GET.get('id_recherche')).lower()
    annonces_list = Produit.objects.none()
    if recherche:
        annonces_list = Produit.objects.filter(Q(nom_produit__lower__icontains=recherche) | Q(description__lower__icontains=recherche)).distinct()

    return render(request, 'chercherForum.html', {'recherche':recherche, 'annonces_list':annonces_list})


@login_required
def chercher_produits(request):
    recherche = str(request.GET.get('id_recherche')).lower()
    if recherche:
        produits_list = Produit.objects.exclude(asso__slug__in=request.user.getListeSlugsAssos_nonmembre()).filter(Q(nom_produit__lower__icontains=recherche) | Q(description__contains=recherche)).distinct().select_subclasses()
    else:
        produits_list = Produit.objects.none()

    return render(request, 'bourseLibre/produit_recherche.html', {'recherche':recherche, 'produits_list':produits_list, })

@login_required
def lireConversation(request, destinataire):
    conversation = getOrCreateConversation(request.user.username, destinataire)
    messages = Message.objects.filter(conversation=conversation).order_by("date_creation")
    paginator = Paginator(messages, 25) # Show 10 contacts per page.
    if not 'page' in request.GET:
        page_number = paginator.num_pages
    else:
        page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    message_defaut = None
    id_panier = request.GET.get('panier')
    if id_panier:
        id_destinataire = Profil.objects.get(username=destinataire).id
        message_defaut = Panier.objects.get(id=id_panier).get_message_demande(int(id_destinataire))

    id_produit = request.GET.get('produit')
    if id_produit:
        message_defaut = Produit.objects.get(id=id_produit).get_message_demande()

    form = MessageForm(request.POST or None, message=message_defaut)
    if form.is_valid():
        message = form.save(commit=False)
        message.conversation = conversation
        message.auteur = request.user
        conversation.date_dernierMessage = message.date_creation
        conversation.dernierMessage =  ("(" + str(message.auteur) + ") " + str(strip_tags(message.message).replace('&nspb',' ')))[:96]
        if len("(" + str(message.auteur) + ") " + str(strip_tags(message.message).replace('&nspb',' '))) > 96:
            conversation.dernierMessage += "..."
        conversation.save()
        message.save()
        url = message.get_absolute_url()
        action.send(request.user, verb='envoi_salon_prive', action_object=conversation, url=url, group=destinataire,
                    description="a envoyé un message privé à " + destinataire)

        profil_destinataire = Profil.objects.get(username=destinataire)
        suivi, created = Suivis.objects.get_or_create(nom_suivi='conversations')
        if profil_destinataire in followers(suivi):
            titre = "Message Privé"
            msg = request.user.username + " vous a envoyé un <a href='https://www.perma.cat" + url.split("#")[0] +"'>" + "message</a>"
            msg_notif = request.user.username + " vous a envoyé un message"
            emails = [profil_destinataire.email, ]
            action.send(request.user, verb='emails', url=url, titre=titre, message=msg, emails=emails)
            payload = {"head": titre, "body": msg_notif,
                       "icon": static('android-chrome-256x256.png'),
                       "url": message.get_absolute_url_site()}
            try:
                send_user_notification(profil_destinataire, payload=payload, ttl=7200)
            except:
                pass
            # try:
            #     send_mail(sujet, message, SERVER_EMAIL, [profil_destinataire.email, ], fail_silently=False,)
            # except Exception as inst:
            #     mail_admins("erreur mails",
            #             sujet + "\n" + message + "\n xxx \n" + str(profil_destinataire.email) + "\n erreur : " + str(inst))
        return redirect(request.path)

    return render(request, 'lireConversation.html', {'conversation': conversation, 'form': form, 'page_obj': page_obj, 'destinataire':destinataire})


@login_required
def partagerPosition(request, slug_conversation):
    form_adresse = AdresseForm4(request.POST or None)
    conversation = Conversation.objects.get(slug=slug_conversation)

    if form_adresse.is_valid():
        adresse = form_adresse.save()
        try :
            url = reverse('voirLieu', kwargs={'id_lieu':adresse.id})
            mess = request.user.username + "<a href='" + url + ">" + \
                   " a partagé une position avec vous</a> (<a href='"+adresse.getGoogleUrl + \
                   "' target='_blank'  rel='noopener noreferrer nofollow'>voir sur google</a>)"
            message = Message(message=mess, conversation=conversation, auteur=request.user)
            message.save()
        except:
            pass

        return redirect(conversation)

    return render(request, 'ajouterLieuConversation.html', {'form': form_adresse, 'destinataire':conversation.get_destinataire(request)})



@login_required
def voirLieu(request, id_lieu):
    lieux = [Adresse.objects.get(id=id_lieu), ]
    titre = lieux[0]
    return render(request, 'carte_adresses.html', {'titre':titre, "lieux":lieux})

@login_required
def voirLieuInfo(request, id_lieu):
    lieux = [Adresse.objects.get(id=id_lieu), ]
    titre = lieux[0]
    return render(request, 'carte_adresses.html', {'titre':titre, "lieux":lieux})

@login_required
def lireConversation_2noms(request, destinataire1, destinataire2):
    if request.user.username==destinataire1:
        return lireConversation(request, destinataire2)
    elif request.user.username==destinataire2:
        return lireConversation(request, destinataire1)
    else:
        return render(request, 'erreur.html', {'msg':"Vous n'êtes pas autorisé à voir cette conversation"})

class ListeConversations(ListView):
    model = Conversation
    context_object_name = "conversation_list"
    template_name = "conversations.html"
    paginate_by = 1

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        dateMin = (datetime.now() - timedelta(days=30)).replace(tzinfo=pytz.UTC)
        context['conversations'] = Conversation.objects.filter(Q(date_dernierMessage__isnull=False, date_dernierMessage__gt=dateMin) & (Q(profil2__id=self.request.user.id) | Q(profil1__id=self.request.user.id))).order_by('-date_dernierMessage')
        context['conversations_archive'] = Conversation.objects.filter(Q(date_dernierMessage__isnull=False, date_dernierMessage__lte=dateMin) & (Q(profil2__id=self.request.user.id) | Q(profil1__id=self.request.user.id))).order_by('-date_dernierMessage')
        context['suivis'], created = Suivis.objects.get_or_create(nom_suivi="conversations")
        context['date_dernieresnotifs'] = self.request.user.date_messages
        self.request.user.date_messages = now()
        self.request.user.save()
        return context

def chercherConversation(request):
    form = ChercherConversationForm(request.user, request.POST or None,)
    profil_autocomplete_form = Profil_rechercheForm(None)
    if form.is_valid():
        destinataire = Profil.objects.get(id=int(form.cleaned_data['destinataire']))
        return redirect('agora_conversation', destinataire=destinataire)

    return render(request, 'chercher_conversation.html', {'form': form, 'profil_autocomplete_form':profil_autocomplete_form})

def profil_autocomplete_recherche(request):
    try:
        destinataire = Profil.objects.get(id=int(request.GET["profil"]))
    except:
        return redirect('conversations')

    return redirect('agora_conversation', destinataire=destinataire)


class ProfilAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Profil.objects.none()

        qs = Profil.objects.filter().order_by("username")

        if self.q:
            qs = qs.filter(Q(username__istartswith=self.q) | Q(username__icontains=self.q)).order_by("username")

        return qs


class ProfilAutocomplete2(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Profil.objects.none()

        qs = Profil.objects.filter().order_by("username")

        if self.q:
            qs = qs.filter(Q(username__istartswith=self.q) | Q(username__icontains=self.q) | Q(last_name__icontains=self.q) | Q(first_name__icontains=self.q)).order_by("username")

        return qs


@login_required
def getNbProduits_expires(request):
    return len(Produit.objects.filter(user=request.user, date_expiration__lt=date.today()))


@login_required
def supprimerProduits_expires_confirmation(request):
    qs = Produit.objects.select_subclasses()
    produits = qs.filter(user=request.user, date_expiration__lt=date.today())
    return render(request, 'bourseLibre/produitexpires_confirm_delete.html', {'produits': produits,})

@login_required
def supprimerProduits_expires(request):
    produits = Produit.objects.filter(user=request.user, date_expiration__lt=date.today())

    for prod in produits:
        prod.delete()

    return redirect('bienvenue')


@login_required
def prochaines_rencontres(request):
    return render(request, 'notifications/prochaines_rencontres.html', {})



@login_required
def mesSuivis(request):
    follows = Follow.objects.filter(user=request.user)
    follows_base, follows_agora, follows_autres, follows_forum = [], [], [], []
    for action in follows:
        if not action.follow_object:
            action.delete()
        elif 'articles' in str(action.follow_object):
            follows_forum.append(action)
        elif 'salon' in str(action.follow_object) and not 'salon_accueil' in str(action.follow_object):
            follows_agora.append(action)
        elif str(action.follow_object) in Choix.suivisPossibles:
            follows_base.append(action)
        elif str(action.follow_object) in Choix.suivisPossibles_groupes:
            follows_base.append(action)
        else:
            follows_autres.append(action)

    return render(request, 'notifications/mesSuivis.html', {'follows_base': follows_base, 'follows_agora':follows_agora, 'follows_forum':follows_forum, 'follows_autres':follows_autres})

@login_required
def supprimerAction(request, actionid):
    try:
        action = Follow.objects.get(id=actionid)
        action.delete()
    except:
        messages.info(request, 'Abonnement introuvable, désolé')

    return redirect('mesSuivis')


@login_required
def mesPublications(request, type_action):
    from photologue.models import Document, Album
    from blog.models import Commentaire
    from jardins.models import Jardin, Grainotheque

    liste = []
    if type_action == "parDate":
        return render(request, 'notifications/mesActions.html', {})
    elif type_action == "articles" :
        liste = Article.objects.filter(auteur=request.user).order_by('-date_creation')
    elif type_action == "commentaires" :
        liste = Commentaire.objects.filter(auteur_comm=request.user).order_by('-date_creation')
    elif type_action == "annonces" :
        liste = Produit.objects.filter(user=request.user).order_by('-date_creation')
    elif type_action == "ateliers" :
        liste = Atelier.objects.filter(auteur=request.user).order_by('-date_creation')
    elif type_action == "projets" :
        liste = Projet.objects.filter(auteur=request.user).order_by('-date_creation')
    elif type_action == "documents" :
        liste = Document.objects.filter(auteur=request.user).order_by('-date_creation')
    elif type_action == "album" :
        liste = Album.objects.filter(auteur=request.user).order_by('-date_creation')
    elif type_action == "suffrages" :
        liste = Suffrage.objects.filter(auteur=request.user).order_by('-date_creation')
    elif type_action == "jardins" :
        liste = Jardin.objects.filter(auteur=request.user).order_by('-date_creation')
    elif type_action == "grainotheque" :
        liste = Grainotheque.objects.filter(auteur=request.user).order_by('-date_creation')

    return render(request, 'notifications/mesPublications.html', {"titre":type_action, 'liste':liste})


@login_required
def mesActions(request):
    return render(request, 'notifications/mesActions.html', {})

@login_required
def agora(request, asso):
    asso = testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied
    suivis, created = Suivis.objects.get_or_create(nom_suivi="agora_" + str(asso.slug))
    messages = MessageGeneral.objects.filter(asso__slug=asso.slug).order_by("date_creation")
    form = MessageGeneralForm(request.POST or None) 
    if form.is_valid(): 
        message = form.save(commit=False) 
        message.auteur = request.user 
        message.asso = asso
        message.save()
        group, created = Group.objects.get_or_create(name='tous')
        url = reverse('agora', kwargs={'asso':asso.slug})
        action.send(request.user, verb='envoi_salon_'+str(asso.slug), action_object=message, target=group, url=url, description="a envoyé un message dans le salon '%s'"%str(asso.nom))

        return redirect(request.path)
    return render(request, 'agora.html', {'form': form, 'messages_echanges': messages, 'asso':asso, 'suivis':suivis})


def testIsMembreSalon(request, slug):
    salon = get_object_or_404(Salon, slug=slug)
    if not salon.est_autorise(request.user) and not request.user.is_superuser:
        return render(request, 'notMembre.html', {'asso':salon.titre } )
    return salon

@login_required
def salon_accueil(request):
    salons_su = []
    salons_inscrit = InscritSalon.objects.filter(profil=request.user, salon__type_salon=1).order_by("salon__titre")
    salons_prives = [s.salon for s in salons_inscrit]
    salons_publics = Salon.objects.filter(type_salon=0).order_by("titre")
    salons_groupes = [s for s in Salon.objects.filter(type_salon=2).order_by("titre") if s.est_autorise(request.user)]

    dateMin = (datetime.now() - timedelta(days=15)).replace(tzinfo=pytz.UTC)
    salons_recents = [s.salon for s in salons_inscrit.filter(Q(salon__date_dernierMessage__gte=dateMin) | Q(salon__date_creation__gte=dateMin)).order_by(Lower("salon__titre"))]
    suivis, created = Suivis.objects.get_or_create(nom_suivi="salon_accueil")
    invit = InvitationDansSalon.objects.filter(profil_invite=request.user).order_by("-date_creation")
    inner_qs = list(set(list(salons_inscrit.values_list('salon__tags', flat=True)) +
                        list( salons_publics.values_list('tags', flat=True).distinct())))
    if inner_qs:
        inner_qs.remove(None)
        if (None, ) in inner_qs:
            inner_qs.remove((None, ))
    tags = Tag.objects.filter(id__in=inner_qs)

    return render(request, 'salon/accueilSalons.html', {'salons_prives':salons_prives, "salons_publics":salons_publics, "salons_groupes":salons_groupes, "salons_recents":salons_recents, "salons_su":salons_su, "invit":invit, "suivis":suivis, "tags":tags })


class ListeSalons(ListView):
    model = Salon
    context_object_name = "salons_list"
    template_name = "salon/index.html"
    paginate_by = 30

    def get_queryset(self):
        self.params = dict(self.request.GET.items())
        salons_publics = Salon.objects.filter(type_salon=0).order_by("titre")
        return salons_publics

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["salons_prives"] = [s.salon for s in InscritSalon.objects.filter(profil=self.request.user, salon__type_salon=1).order_by("salon__titre").distinct()]
        suivis, created = Suivis.objects.get_or_create(nom_suivi="salon_accueil")
        context["invit"] = InvitationDansSalon.objects.filter(profil_invite=self.request.user).order_by("salon__titre")

        #context["webpush"] = {"group": group_name }
        if self.request.user.is_superuser:
            context["salons_su"] = Salon.objects.all().order_by("-titre")

        return context



@login_required
def salon(request, slug):
    invit = InvitationDansSalon.objects.filter(salon__slug=slug, profil_invite=request.user)
    if invit:
        return redirect(reverse('invitationDansSalon', kwargs={'slug_salon': slug}))

    salon = testIsMembreSalon(request, slug)
    if not isinstance(salon, Salon):
        raise PermissionDenied
    dates = EvenementSalon.objects.filter(salon=salon)
    suivis = salon.getSuivi()
    inscrits = salon.getInscrits()
    invites = salon.getInvites()
    jointure_articles = AssociationSalonArticle.objects.filter(salon=salon).order_by('salon__titre')
    messages = Message_salon.objects.filter(salon=salon).order_by("date_creation")
    paginator = Paginator(messages, 100) # Show 100 contacts per page.
    if not 'page' in request.GET:
        page_number = paginator.num_pages
    else:
        page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    form = Message_salonForm(request.POST or None)
    if form.is_valid():
        message = form.save(commit=False)
        message.auteur = request.user
        message.salon = salon
        salon.date_dernierMessage = timezone.now()
        salon.save()
        message.save()
        group, created = Group.objects.get_or_create(name='salon_' + salon.slug)
        url = message.get_absolute_url()
        if salon.estPublic:
            action.send(request.user, verb='envoi_salon_public'+str(salon.slug),
                        action_object=message, target=group, url=url,
                        description="a envoyé un message dans le salon [public] '" + str(salon.titre))
        else:
            action.send(request.user, verb='envoi_salon_'+str(salon.slug),
                        action_object=message, target=group, url=url,
                        description="a envoyé un message dans le salon '" + str(salon.titre) + "' (>"+" ".join([str(x) for x in inscrits])+")")

        emails = [suiv.email for suiv in followers(suivis) if request.user != suiv ]
        message_notif = "Le <a href='" + salon.get_absolute_url_site + "'> Salon '" + salon.titre + "'</a>' a été commenté"

        action.send(salon, verb='emails', url=salon.get_absolute_url(), titre="Salon commenté", message=message_notif, emails=emails)

        payload = {"head": "Salon " + salon.titre, "body": "Nouveau message de " + request.user.username , "icon":static('android-chrome-256x256.png'), "url":message.get_absolute_url_site}
        for suiv in followers(suivis):
            if request.user != suiv:
                try:
                    send_user_notification(suiv, payload=payload, ttl=7200)
                except:
                    pass
        return redirect(request.path)

    return render(request, 'salon/lireSalon.html', {'form': form, 'messages_echanges': messages, 'salon':salon, 'suivis':suivis, "inscrits":inscrits, "invites":invites, "jointure_articles":jointure_articles, "dates":dates, "page_obj":page_obj})

@login_required
def creerSalon(request):
    from bourseLibre.views_inscriptions import suivre_salon
    form = SalonForm(request.POST or None)
    if form.is_valid():
        salon = form.save(request)
        group, created = Group.objects.get_or_create(name='salon_' + salon.slug)
        request.user.groups.add(group)
        message = Message_salon.objects.create(
            salon=salon,
            message=request.user.username + " a créé le salon",
            auteur=get_object_or_404(Profil, username="bot_permacat"),
            date_creation=now()).save()
        form.save_m2m()
        suivre_salon(request, salon.slug)

        if salon.estPublic:
            url = reverse('salon', kwargs={'slug':salon.slug})
            action.send(request.user, verb='creation_salon_public_'+str(salon.slug), action_object=salon, target=group, url=url, description="a créé un nouveau salon public: " + str(salon.titre))

        return redirect(salon.get_absolute_url())
    return render(request, 'salon/creerSalon.html', {'form': form})

@login_required
def modifierSalon(request, slug):
    salon = testIsMembreSalon(request, slug)
    if not isinstance(salon, Salon):
        raise PermissionDenied

    form = ModifierSalonDesciptionForm(request.POST or None, instance=salon)
    if form.is_valid():
        salon = form.save(commit=False)

        message = Message_salon.objects.create(
            salon=salon,
            message=request.user.username + " a modifié la description du salon",
            auteur=get_object_or_404(Profil, username="bot_permacat"),
            date_creation=now()).save()

        form.save_m2m()

        if salon.estPublic:
            url = reverse('salon', kwargs={'slug':salon.slug})
            action.send(request.user, verb='creation_salon_public_'+str(salon.slug), action_object=salon, url=url, description="a créé un nouveau salon public: " + str(salon.titre))

        return redirect(salon.get_absolute_url())
    return render(request, 'salon/modifierSalon.html', {'form': form, 'salon':salon})

class ModifierSalonClass(UpdateView):
    model = Salon
    form_class = ModifierSalonDesciptionForm

    def get_object(self):
        return Salon.objects.get(slug=self.kwargs['slug'])


@login_required
def invitationDansSalon(request, slug_salon):
    salon = get_object_or_404(Salon, slug=slug_salon)
    invit = InvitationDansSalon.objects.filter(salon=salon, profil_invite=request.user)
    if request.POST:
        if "annuler" not in request.POST:
            p, message = Message_salon.objects.get_or_create(
                salon=salon,
                message="%s a accepté l'invitation. Bienvenue !"%request.user,
                auteur=get_object_or_404(Profil, username="bot_permacat"),
                date_creation=now())
            p, inscription = InscritSalon.objects.get_or_create(salon=salon, profil=request.user)
            group, created = Group.objects.get_or_create(name='salon_' + salon.slug)
            request.user.groups.add(group)
            suivi, created = Suivis.objects.get_or_create(nom_suivi='salon_' + str(slug_salon))
            if suivi in following(request.user):
                actions.unfollow(request.user, suivi)
            else:
                actions.follow(request.user, suivi, actor_only=True, send_action=False)
        else:
            message = Message_salon.objects.create(
                salon=salon,
                message="%s a décliné l'invitation."%request.user,
                auteur=get_object_or_404(Profil, username="bot_permacat"),
                date_creation=now()).save()
        for i in invit:
            stream = action_object_stream(i)
            for j in stream:
                j.delete()
            i.delete()
        return redirect(salon.get_absolute_url())

    return render(request, 'salon/invitationSalon.html', {'salon': salon, "invit": invit})

@login_required
def inviterDansSalon(request, slug_salon):
    salon = testIsMembreSalon(request, slug_salon)
    #form = InviterDansSalonForm(salon, request.POST or None)
    form = Profil_recherche2Form(request, salon, request.POST or None)
    if form.is_valid():
        invite = form.cleaned_data['profil']#get_object_or_404(Profil, id=int(form.cleaned_data['profil']))
        if 'voirprofil' in request.POST:
            return render(request, 'salon/inviterDansSalon.html', {'form': form, 'salon':salon, 'invite':invite})
        else:
            if not InvitationDansSalon.objects.filter(salon=salon, profil_invite=invite, profil_invitant=request.user).count():
                invitation = InvitationDansSalon(salon=salon, profil_invite=invite, profil_invitant=request.user)
                invitation.save()
                message = Message_salon.objects.create(
                    salon=salon,
                    message="%s a invité %s."%(invitation.profil_invitant, invitation.profil_invite),
                    auteur=get_object_or_404(Profil, username="bot_permacat"),
                    date_creation=now()).save()
            return redirect(salon.get_absolute_url())
    return render(request, 'salon/inviterDansSalon.html', {'form': form, 'salon':salon})

@login_required
def sortirDuSalon(request, slug_salon):
    salon = testIsMembreSalon(request, slug_salon)
    inscription = InscritSalon.objects.filter(salon=salon, profil=request.user)
    inscription.delete()
    message = Message_salon.objects.create(
        salon=salon,
        message="%s a quitté le salon"%(request.user),
        auteur=get_object_or_404(Profil, username="bot_permacat"),
        date_creation=now()).save()
    return redirect("salon_accueil")


@login_required
def ajouterEvenementSalon(request, slug_salon):
    form = EvenementSalonForm(request.POST or None)

    if form.is_valid():
        ev = form.save(request, slug_salon)
        return redirect(ev.salon)

    return render(request, 'blog/ajouterEvenement.html', {'form': form, })


class SupprimerEvenementSalon(DeleteAccess, DeleteView):
    model = EvenementSalon
    template_name_suffix = '_supprimer'

    def get_object(self):
        return EvenementSalon.objects.get(id=self.kwargs['id_evenementSalon'])

    def get_success_url(self):
        return Salon.objects.get(slug=self.kwargs['slug_salon']).get_absolute_url()



@login_required
def modifier_message(request, id, type_msg, asso, ):
    if type_msg == 'conversation':
        obj = Message.objects.get(id=id)
    elif type_msg == 'salon':
        obj = Message_salon.objects.get(id=id)
    else:
        asso = testIsMembreAsso(request, asso)
        if not isinstance(asso, Asso):
            raise PermissionDenied
        obj = MessageGeneral.objects.get(id=id, asso=asso)

    form = MessageChangeForm(request.POST or None, instance=obj)

    if form.is_valid():
        object = form.save()
        if object.message and object.message !='<br>'and object.message !='<p><br></p>':
            object.date_modification = now()
            object.save()
            return redirect(object.get_absolute_url())
        else:
            object.delete()
            return redirect(obj.get_absolute_url())

    return render(request, 'modifierCommentaire.html', {'form': form, })

class ModifierMessageAgora(UpdateView):
    model = MessageGeneral
    form_class = MessageChangeForm
    template_name = 'modifierCommentaire.html'

    def get_object(self):
        if self.kwargs['type_msg'] == 'conversation':
            obj = Message.objects.get(id=self.kwargs['id'])
            self.redirect_url = obj.conversation.get_absolute_url()
        elif self.kwargs['type_msg'] == 'salon':
            obj = Message_salon.objects.get(id=self.kwargs['id'])
            self.redirect_url = obj.salon.get_absolute_url()
        else:
            self.asso = testIsMembreAsso(self.request, self.kwargs['asso'])
            if not isinstance(self.asso, Asso):
                raise PermissionDenied
            obj = MessageGeneral.objects.get(id=self.kwargs['id'], asso=self.asso)
        return obj

    def form_valid(self, form):
        self.object = form.save()
        if self.object.message and self.object.message !='<br>' and self.object.message !='<p><br></p>':
            self.object.date_modification = now()
            self.object.save()
            return HttpResponseRedirect(self.object.get_absolute_url())
        else:
            self.object.delete()
            if self.kwargs['type_msg'] == 'conversation' or self.kwargs['type_msg'] == 'salon':
                return redirect(self.redirect_url)
            else:
                return reverse('agora', kwargs={'asso':self.asso.slug})

    def form_invalid(self, form):
        if (form.data['message'] == '' or form.data['message'] == '<br>' or form.data['message'] == '<p><br></p>'):
            url = self.object.get_absolute_url()
            self.object.delete()
            return HttpResponseRedirect(url)

        return super(ModifierMessageAgora, self).form_invalid(form)



@login_required
def accesfichier(request, path):
    response = HttpResponse()
    # Content-type will be detected by nginx
    del response['Content-Type']
    response['X-Accel-Redirect'] = '/protected/media/' + path
    return response



class Favoris_list(ListView):
    model = Favoris
    template_name = "favoris/mesFavoris.html"
    ordering = ("nom")


    def get_queryset(self):
        return Favoris.objects.filter(profil=self.request.user).distinct().order_by('nom')


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        return context


class Favoris_supprimer(DeleteView):
    model = Favoris
    template_name = 'favoris/favoris_supprimer.html'

    def get_success_url(self):
        return reverse('mesFavoris')

    def get_object(self):
        ad = Favoris.objects.get(pk=self.kwargs['pk'])
        return ad


class Favoris_update(UpdateView):
    model = Favoris
    template_name = 'favoris/favoris_modifier.html'
    fields = ["nom", "url"]

    def get_success_url(self):
        return reverse('mesFavoris')

@login_required
def favoris_ajouter(request):
    form = FavorisForm(request.POST or None)
    if form.is_valid():
        fav = form.save(request)
        return redirect(reverse("mesFavoris"))

    return render(request, 'favoris/favoris_ajouter.html', {"form": form})


@login_required
def switchThemeSombre(request):
    request.user.css_dark = not request.user.css_dark
    request.user.save()

    return redirect(request.GET.get("next", "bienvenue"))

def getTestLanguage(request):
    from bourseLibre import settings
    return {
        'get_language()':translation.get_language(),
            'chemin':len(settings.LOCALE_PATHS) > 0,
            'trad Publier':translation.gettext("Publier") ,
            'trad Publicar':translation.gettext("Publicar"),
            'cat ok': 'ca' in translation.trans_real.get_languages(),
            'fr ok': 'fr' in translation.trans_real.get_languages(),
            #curl 'http://localhost:8000' -H 'Accept-Language: ja'translation.get_language(),
            'info fr': translation.get_language_info('fr'),
            'info cat':translation.get_language_info('ca'),
            'check fr':translation.check_for_language('fr'),
            'check ca':translation.check_for_language('ca'),
            'to_locale':translation.to_locale('ca'),
            'to_language':translation.to_language('ca'),
            "gettext('Catalan')":translation.gettext('Catalan'),
            "gettext('Publier')":translation.gettext('Publier')
            }

@login_required
def switchLanguage(request):

    if translation.get_language() == "fr":
        translation.activate("ca")
        request.user.language = "ca"
    else:
        translation.activate("fr")
        request.user.language = "fr"

    return redirect(request.GET.get("next", "bienvenue"))


def ducepaujus(request):
    if request.user.is_anonymous:
        form = ContactMailForm(request.POST or None, )
    else:
        form = ContactForm(request.POST or None, )

    if form.is_valid():
        if request.user.is_anonymous:
            envoyeur = "Anonyme : " + form.cleaned_data['email']
            email = form.cleaned_data['email']
        else:
            envoyeur = request.user.username + " (" + request.user.email + ") "
            email = request.user.email
            
        sujet = form.cleaned_data['sujet']
        message_txt = envoyeur + " a envoyé le message suivant : " + form.cleaned_data['msg']
        message_html = envoyeur + " a envoyé le message suivant : " + form.cleaned_data['msg']
        # MessageAdmin.objects.create(email=email, message=message_txt, sujet=sujet)
        #
        # admin = Profil.objects.get(username="Eloi")
        # if request.user.is_anonymous:
        #     action.send(admin, verb='envoi_salon_prive', url="/gestion/bourseLibre/messageadmin/",
        #                 description="a envoyé un message aux admin (%s)" % admin.username)
        # else:
        #     action.send(request.user, verb='envoi_salon_prive', url="/gestion/bourseLibre/messageadmin/",
        #                 description="a envoyé un message aux admin (%s)" % admin.username)

        try:
            envoiMailAdmin = True
            if envoiMailAdmin and not LOCALL:
                if request.user.is_anonymous:
                    send_mail(sujet, "Vous avez envoyé à PermAgora le message suivant : " + message_html, SERVER_EMAIL, ["permagora66@gmail.com",], fail_silently=False, html_message=message_html)
                else:
                    send_mail(sujet, "Vous avez envoyé à PermAgora le message suivant : " + message_html, SERVER_EMAIL, ["permagora66@gmail.com",], fail_silently=False, html_message=message_html)

            return render(request, 'contact/message_envoye.html', {'sujet': sujet, 'msg': message_html,
                                                   'envoyeur': envoyeur ,
                                                   "destinataire": "administrateurs "})
        except BadHeaderError:
            return render(request, 'erreur.html', {'msg':'Invalid header found.'})

        return render(request, 'contact/message_envoye.html',
                      {'sujet': sujet, 'msg': message_html, 'envoyeur': envoyeur,
                       "destinataire": "administrateurs "})

    return render(request, 'ducepaujus.html', {"form": form})
