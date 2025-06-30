import re

from django.shortcuts import render, redirect, reverse
#from django.urls import reverse_lazy
#from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView
#from django.contrib.auth.decorators import login_required
#from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, HttpResponseRedirect
#import csv
from django.db.models import Q
from bourseLibre.settings import PROJECT_ROOT, os
from bourseLibre.settings.production import LOCALL
from .forms import (AdhesionForm, AdherentForm, AdherentChangeForm,  AdherentForm_conf66, AdherentChangeForm_conf66,
                InscriptionMail_complet_Form, InscriptionMail_Mail_Form, InscriptionMailForm, ListeDiffusionForm,
    InscriptionMail_listeAdherent_Form, InscriptionMailAdherentALsteForm, AdhesionForm_adherent, Comm_adh_form,
    Contact_form, Contact_update_form, ContactContact_form)
from .models import (Adherent, Adhesion, InscriptionMail, Contact, ContactContact,
                     ListeDiffusion, Comm_adherent, ProjetPhoning)
from bourseLibre.models import Adresse, Profil, Asso, Adhesion_asso
from bourseLibre.views import testIsMembreAsso
from .filters import AdherentsCarteFilter, ContactCarteFilter
#from .constantes import get_slug_salon
from django.utils.timezone import now
from actstream.models import Action
from datetime import date, timedelta, datetime


from django.http import HttpResponse
from django.template import loader

from django.contrib.auth.decorators import login_required, user_passes_test
#from bourseLibre.models import Salon, InscritSalon
from django.contrib.auth.mixins import UserPassesTestMixin
from actstream import actions, action

def is_membre_bureau(user, asso_slug="conf66"):
    if user.is_anonymous:
        return False
    return user.estmembre_bureau(asso_slug)


@login_required
def set_projet_phoning(request, asso_slug, url_redirect):
    projet = get_object_or_404(ProjetPhoning, slug=asso_slug)
    request.session['projet_courant'] = projet
    return redirect(url_redirect)


class ListeAdherents(UserPassesTestMixin, ListView):
    model = Adherent
    context_object_name = "adherents"
    template_name = "adherents/carte_adherents.html"

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        self.request.session["asso_slug"] = self.asso.slug
        return self.request.user.isCotisationAJour(self.asso.slug) or self.request.user.is_superuser

    def get_queryset(self):
        params = dict(self.request.GET.items())

        if "lettre" in self.request.GET:
            qs = Adherent.objects.filter(asso=self.asso, nom__istartswith=self.request.GET["lettre"]).order_by("nom")
        else:
            qs = Adherent.objects.filter(asso=self.asso).order_by("nom")
        profils_filtres = AdherentsCarteFilter(self.request.GET, queryset=qs)
        self.qs = profils_filtres.qs.distinct()
        return self.qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context['asso_slug'] = self.asso.slug
        context['titre'] = "Adhérents " +self.asso.nom +" (%d)" % len(qs)
        filter = AdherentsCarteFilter(self.request.GET, qs)
        context["filter"] = filter
        context['is_membre_bureau'] = is_membre_bureau(self.request.user, self.asso.slug)
        context['historique'] = Action.objects.filter(Q(verb__startswith='adherent_' +self.asso.slug+'_'))
        return context


    def get_template_names(self, *args, **kwargs):
        # Check if the request path is the path for a-url in example app
        if self.asso.slug == "conf66":
            return "adherents/carte_adherents_" + self.asso.slug + ".html"
        else:
            return "adherents/carte_adherents.html"

class AdherentDetailView(UserPassesTestMixin, DetailView, ):
    model = Adherent
    template_name_suffix = '_detail'

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        self.request.session["asso_slug"] = self.asso.slug
        return self.request.user.isCotisationAJour(self.asso.slug) or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['adhesions'] = Adhesion.objects.filter(adherent=self.object).order_by("-date_cotisation__year", "adherent__nom")
        context['inscriptionsMail'] = InscriptionMail.objects.filter(adherent=self.object)
        context['is_membre_bureau'] = self.request.user.estmembre_bureau(self.asso.slug)
        context['asso_slug'] = self.asso.slug
        if context['is_membre_bureau']:
            context['commentaires'] = Comm_adherent.objects.filter(adherent=self.object)
        return context


    def get_template_names(self, *args, **kwargs):
        # Check if the request path is the path for a-url in example app
        if self.asso.slug == "conf66":
            return "adherents/adherent_" + self.asso.slug + "_detail.html"
        else:
            return "adherents/adherent_detail.html"

def monProfil(request, asso_slug):
    adherents = Adherent.objects.filter(profil=request.user, asso__slug=asso_slug)
    if not adherents.exists():
        return render(request, 'adherents/profil_inconnu.html', {"asso_slug":asso_slug})

    return redirect('adherents:adherent_detail', pk=adherents[0].pk, asso_slug=asso_slug)

class AdherentDeleteView(UserPassesTestMixin, DeleteView):
    model = Adherent
    template_name_suffix = '_supprimer'

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        return is_membre_bureau(self.request.user, self.asso.slug)

    def get_success_url(self):
        desc = " a supprimé l'adhérent : " + str(self.object.nom) + ", " + str(self.object.prenom)
        action.send(self.request.user, verb="adherent_"+self.asso.slug+"_supprimer", url=reverse('adherents:accueil'), description=desc)
        return reverse('adherents:accueil')

class AdherentUpdateView(UserPassesTestMixin, UpdateView):
    model = Adherent
    template_name_suffix = '_modifier'
    form_class = AdherentChangeForm

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        return is_membre_bureau(self.request.user, self.asso.slug) or self.request.user == self.object.profil or self.request.user.is_superuser


    def form_valid(self, form):
        desc = " a modifié l'adhérent : " + str(self.object.nom) + ", " + str(self.object.prenom)+ " (" + str(
            form.changed_data) + ")"
        action.send(self.request.user, verb='adherent_'+self.asso.slug+'_modifier', action_object=self.object,
                    url=self.object.get_absolute_url(), description=desc)
        titre = "[PCAT_adherents] Modification de l'adherent : " + str(self.object)
        if self.asso.email:
            action.send(self.request.user, verb='emails', url=self.object.get_absolute_url(), titre=titre, message=str(self.request.user) + desc, emails=[self.asso.email, ])
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_form_class(self):
        if self.asso.slug == "conf66":
            return AdherentChangeForm_conf66
        else:
            return AdherentChangeForm

class AdherentAdresseUpdateView(UserPassesTestMixin, UpdateView):
    model = Adresse
    template_name_suffix = '_modifier'
    fields = ["rue", "code_postal", "commune", "latitude", "longitude", "telephone"]

    def test_func(self):
        self.adresse = Adresse.objects.get(pk=self.kwargs['pk'])
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        self.adherent = self.adresse.adherent_set.first()
        return is_membre_bureau(self.request.user, self.asso.slug) or self.request.user == self.adherent.profil

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return self.adherent.get_absolute_url()

    def form_valid(self, form):
        desc =" a modifié l'adresse de l'adhérent : " + str(self.adherent) + " (" + str(form.changed_data)+ ")"
        action.send(self.request.user, verb="adherent_"+self.asso.slug+"_modifAdresse", action_object=self.object, url=self.adherent.get_absolute_url(), description=desc)
        titre = "[PCAT_adherents] Modification de l'adresse de l'adherent" + str(self.adherent)
        action.send(self.request.user, verb='emails', url=self.adherent.get_absolute_url(), titre=titre, message=str(self.request.user) + desc, emails=[self.asso.email, ])
        return super().form_valid(form)



@login_required
def adherent_ajouter(request, asso_slug):
    asso = testIsMembreAsso(request, asso_slug)

    if asso_slug == "conf66":
        form = AdherentForm_conf66(request.POST or None)
    else:
        form = AdherentForm(request.POST or None)
    if form.is_valid():
        adresse = Adresse.objects.create(
            rue=form.cleaned_data['rue'],
            code_postal=form.cleaned_data['code_postal'],
            commune=form.cleaned_data['commune'],
            telephone=form.cleaned_data['telephone'],
        )
        adherent = form.save(commit=False)
        adherent.adresse = adresse
        adherent.asso = asso
        adherent = form.save()
        desc = " a ajouté l'adhérent : " + str(adherent.nom) + ", " + str(adherent.prenom)
        action.send(request.user, verb='adherent_'+ asso_slug +'_ajouter', action_object=adherent, url=adherent.get_absolute_url(), description=desc)
        titre = "[PCAT_adherents] Ajout de l'adherent : " + str(adherent)
        action.send(request.user, verb='emails', url=adherent.get_absolute_url(), titre=titre,
                    message=str(request.user) + desc, emails=['confederationpaysanne66@gmail.com', ])

        return redirect(adherent)

    return render(request, 'adherents/adherent_ajouter.html', {"form": form, "asso_slug":asso_slug})

@login_required
def creerAdherent(telephone, asso, nom=None, prenom=None, email=None, rue=None, commune=None, code_postal=None, profil=None):
    if not(telephone or nom or prenom or email or code_postal):
        return 0, None

    if not Adherent.objects.filter(adresse__code_postal=code_postal,
                                 adresse__telephone=telephone,
                                nom=nom,
                                prenom=prenom,
                                email=email,
                                   asso=asso).exists():
        if code_postal and telephone:
            adresse, created = Adresse.objects.get_or_create(
                                        telephone=telephone,
                                        commune=commune,
                                        code_postal=code_postal,
                                        rue=rue,
                                        )
        else:
            adresse = Adresse.objects.create(
                                        telephone=telephone,
                                            commune=commune,
                                            code_postal=code_postal,
                                            rue=rue,
                                        )
        p, created = Adherent.objects.get_or_create(
                                        nom=nom,
                                        prenom=prenom,
                                        email=email,
                                        adresse=adresse,
                                        profil=profil,
                                        asso=asso
                                    )
        if created:
            for a in Adhesion_asso.objects.filter(user=profil):
                Adhesion.objects.get_or_create(
                    adherent=p,
                    montant=a.montant,
                    date_cotisation=a.date_cotisation,
                    moyen=a.moyen,
                    detail=a.detail,
                    asso=asso
                )

        return 1, p
    return 0, None


@login_required
def ajouterLesMembresGroupe(request, asso_slug ):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    asso = testIsMembreAsso(request, asso_slug)
    profils = asso.getProfils()
    m = ""
    j=0
    for i, adherent in enumerate(profils):
        #if j>5 or i> 200:
         #   break

        res, p = creerAdherent(telephone=adherent.adresse.telephone if adherent.adresse.telephone else None,
                             asso=asso,
                             nom=adherent.last_name,
                             prenom=adherent.first_name,
                             email=adherent.email,
                             rue=adherent.adresse.rue,
                             commune=adherent.adresse.commune,
                             code_postal=adherent.adresse.code_postal,
                             profil=adherent
                             )
        if res:
            m += "<p>ajout " + str(adherent) +"</p>"
            j += 1
        else:
            m += "<p>refus " + str(adherent) +"</p>"


    return redirect("adherents:adherent_liste", {"asso_slug":asso_slug})

class ListeAdhesions(UserPassesTestMixin, ListView):
    model = Adhesion
    context_object_name = "adhesions"
    template_name = "adherents/adhesion_liste.html"
    ordering = ("-date_cotisation__year", "adherent__nom")

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        return is_membre_bureau(self.request.user, self.asso.slug)

    def get_queryset(self):
        return Adhesion.objects.filter(asso=self.asso).order_by("-date_cotisation")
        #params = dict(self.request.GET.items())

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context


class AdhesionDetailView(UserPassesTestMixin, DetailView):
    model = Adhesion

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        return is_membre_bureau(self.request.user, self.asso.slug)

class AdhesionDeleteView(UserPassesTestMixin, DeleteView):
    model = Adhesion
    template_name_suffix = '_supprimer'

    def get_success_url(self):
        return self.adherent.get_absolute_url()

    def get_object(self):
        ad = Adhesion.objects.get(pk=self.kwargs['pk'])
        self.adherent = ad.adherent
        return ad

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        return is_membre_bureau(self.request.user, self.asso.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context

class AdhesionUpdateView(UserPassesTestMixin, UpdateView):
    model = Adhesion
    template_name_suffix = '_modifier'
    fields = ["date_cotisation", "montant", "moyen", "detail"]

    def get_success_url(self):
        return self.object.adherent.get_absolute_url()


    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        return is_membre_bureau(self.request.user, self.asso.slug)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context

def ajouterAdhesion(request, asso_slug, adherent_pk):
    asso = testIsMembreAsso(request, asso_slug,)
    if not is_membre_bureau(request.user):
        return HttpResponseForbidden()

    form = AdhesionForm(request.POST or None)
    adherent = get_object_or_404(Adherent,  asso__slug=asso_slug, pk=adherent_pk)
    if form.is_valid():
        adhesion = form.save(commit=False)
        adhesion.adherent = adherent
        adhesion.asso = asso
        adhesion.save()
        return redirect(adherent)

    return render(request, 'adherents/adhesion_ajouter.html', {"form": form, 'adherent': adherent, "asso_slug":asso_slug})


def ajouterAdhesion_2(request,  asso_slug, ):
    asso = testIsMembreAsso(request,  asso_slug, )
    if not is_membre_bureau(request.user, asso_slug):
        return HttpResponseForbidden()

    form = AdhesionForm_adherent(asso_slug, request.POST or None)
    if form.is_valid():
        adhesion = form.save(commit=False)
        adhesion.asso = asso
        adhesion.save()
        return redirect(adhesion.adherent)

    return render(request, 'adherents/adhesion_ajouter.html', {"form": form, "asso_slug":asso_slug})


login_required
def normaliser_adherents(request, asso_slug):
    """A view that streams a large CSV file."""
    if not is_membre_bureau(request.user, asso_slug):
        return HttpResponseForbidden()
    # profils = Adherent.objects.all()
    # for p in profils:
    #     if p.prenom:
    #         p.nom = str.upper(p.nom)
    #         p.save()
    #
    # for a in  Adhesion.objects.all():
    #     if "ch" in a.moyen:
    #         a.moyen = "CHQ"
    #         a.save()
    #     elif "virement" in a.moyen or a.moyen == "vitrment":
    #         a.moyen = "VIR"
    #         a.save()
    #     elif a.moyen == "èspèces" or "espèce" in a.moyen :
    #         a.moyen = "ESP"
    #         a.save()

    for a in Adherent.objects.all():
        if not "@" in a.email:
            a.email = ""
            a.save()

    return render(request, "adherents/accueil_admin.html", {'msg':"Tout est pret", "asso_slug":asso_slug})

login_required
def get_csv2(request, asso_slug):
    if not is_membre_bureau(request.user, asso_slug):
        return HttpResponseForbidden()
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(
        content_type="text/csv",
    )
    response['Content-Disposition'] = 'attachment; filename="myfile.csv"'

    # The data is hard-coded here, but you could load it from a database or
    # some other source.
    csv_data = [
        ("NOM PRENOM","STATUT","APE", "ADRESSE POSTALE","ADRESSE MAIL","TELEPHONE","MONTANT2020","MOYEN2020","MONTANT2021","MOYEN2021","MONTANT2022","MOYEN2022","MONTANT2023","MOYEN2023"),]
    csv_data += [(a.nom +" "+ a.prenom, a.statut, a.production_ape,a.adresse.code_postal+ " " + a.adresse.commune,  a.email, a.adresse.telephone, a.get_adhesion_an(2020).montant,
          a.get_adhesion_an(2020).montant, a.get_adhesion_an(2021).montant, a.get_adhesion_an(2021).montant, a.get_adhesion_an(2022).montant, a.get_adhesion_an(2022).montant, a.get_adhesion_an(2023).montant, a.get_adhesion_an(2023).montant) for a in Adherent.objects.all() ]

    t = loader.get_template("my_template_name.csv")
    c = {"data": csv_data}
    response.write(t.render(c))
    return response

import csv

from django.http import StreamingHttpResponse

class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value


login_required
def write_csv_data(request, csv_data):
    """A view that streams a large CSV file."""
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    return StreamingHttpResponse(
        (writer.writerow(row) for row in csv_data),
        content_type="text/csv",
    )

login_required
def get_csv_adherents(request, asso_slug):
    """A view that streams a large CSV file."""
    if not is_membre_bureau(request.user, asso_slug):
        return HttpResponseForbidden()
    profils = Adherent.objects.filter(asso__slug=asso_slug).order_by("nom")
    profils_filtres = AdherentsCarteFilter(request.GET, queryset=profils)
    current_year = date.today().isocalendar()[0]

    csv_data = [
        ("NOM","PRENOM","GAEC","STATUT(0?-1AP-2ATS-3CC-4Retraite-5ATS-6PP)","APE", "ADRESSE POSTALE","CODE POSTAL","COMMUNE","ADRESSE MAIL","TELEPHONE","PROFIL_PCAT","MONTANT2020","MOYEN2020","MONTANT2021","MOYEN2021","MONTANT2022","MOYEN2022","MONTANT2023","MOYEN2023","MONTANT2024","MOYEN2024"),]
    csv_data += [(a.nom, a.prenom, a.nom_gaec, a.get_statut_display(), a.production_ape,a.adresse.rue,a.adresse.code_postal,a.adresse.commune,  a.email, a.adresse.telephone, a.get_profil_username,
                  a.get_adhesion_an(current_year-4).montant, a.get_adhesion_an(current_year-4).moyen,
                  a.get_adhesion_an(current_year-3).montant, a.get_adhesion_an(current_year-3).moyen,
                  a.get_adhesion_an(current_year-2).montant, a.get_adhesion_an(current_year-2).moyen,
                  a.get_adhesion_an(current_year-1).montant, a.get_adhesion_an(current_year-1).moyen,
                  a.get_adhesion_an(current_year).montant, a.get_adhesion_an(current_year).moyen) for a in profils_filtres.qs.distinct() ]

    return write_csv_data(request, csv_data)

login_required
def get_csv_adherents_pasajour(request, asso_slug):
    """A view that streams a large CSV file."""
    if not is_membre_bureau(request.user, asso_slug):
        return HttpResponseForbidden()
    profils = Adherent.objects.filter(asso__slug=asso_slug).order_by("nom").distinct()
    current_year = date.today().isocalendar()[0]

    csv_data = [ ("Email"),]
    csv_data += list(set([(a.email, ) for a in profils if not a.get_adhesion_an(current_year).montant]))

    return write_csv_data(request, csv_data)

login_required
def get_csv_listeMails(request, asso_slug):
    """A view that streams a large CSV file."""
    if not is_membre_bureau(request.user, asso_slug):
        return HttpResponseForbidden()
    profils = Adherent.objects.filter(asso__slug=asso_slug).order_by("nom")

    csv_data = [("Name","Given Name","Additional Name","Family Name","Yomi Name","Given Name Yomi","Additional Name Yomi",
                 "Family Name Yomi","Name Prefix","Name Suffix","Initials","Nickname","Short Name","Maiden Name","Birthday",
                 "Gender","Location","Billing Information","Directory Server","Mileage","Occupation","Hobby","Sensitivity",
                 "Priority","Subject","Notes","Language","Photo","Group Membership","E-mail 1 - Type","E-mail 1 - Value",
                 "E-mail 2 - Type","E-mail 2 - Value","Phone 1 - Type","Phone 1 - Value","Phone 2 - Type","Phone 2 - Value",
                 "Address 1 - Type","Address 1 - Formatted","Address 1 - Street","Address 1 - City","Address 1 - PO Box",
                 "Address 1 - Region","Address 1 - Postal Code","Address 1 - Country","Address 1 - Extended Address",
                 "Organization 1 - Type","Organization 1 - Name","Organization 1 - Yomi Name","Organization 1 - Title",
                 "Organization 1 - Department","Organization 1 - Symbol","Organization 1 - Location","Organization 1 - Job Description")]
   
    csv_data += [(profil.nom + " " + profil.prenom,"","","","","","","","","","","","","","","","","","","","","","","","","","","",
                    profil.getInscriptions_listeMails_csvggl(),"",profil.email,"","","",profil.adresse.telephone,
                  "","","","","","","","","","","","","","","","","","") for profil in profils if profil.get_inscriptionsMail]

    return write_csv_data(request, csv_data)




@login_required
def accueil_admin(request, asso_slug):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    return render(request, "adherents/accueil_admin.html", {'msg':"Tout est pret : asso " + asso_slug, "asso_slug":asso_slug})


def get_dossier_db(nomfichier):
    if LOCALL:
        return "/home/tchenrezi/Téléchargements/" + nomfichier
    return os.path.abspath(os.path.join(PROJECT_ROOT, "../../", nomfichier))

@login_required
def modif_APE(request, asso_slug):
    if not is_membre_bureau(request.user, asso_slug):
        return HttpResponseForbidden()
    msg = ""
    for a in Adherent.objects.filter(production_ape__isnull=False):
        old = str(a.production_ape)
        if len(str(a.production_ape).split("PE "))>1:
            a.production_ape = str(a.production_ape).split("PE ")[1]
            a.save()
            msg += str(a.production_ape) + " from " + old + "\n"
    return render(request, "adherents/accueil_admin.html", {'msg':"Tout est pret"})



def get_statut(nom):
    if nom == "AP":
        return "1"
    elif nom == "CS":
        return "2"
    elif nom == "CC":
        return "3"
    elif nom == "retraité" or nom == "retraitée"  or nom == "retraité.e" :
        return "4"
    elif nom == "ATS" :
        return "5"
    elif nom == "PP" :
        return "6"
    return "0"


@login_required
def import_adherents_ggl(request, asso_slug):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    asso = testIsMembreAsso(request, asso_slug)
    params = dict(request.GET.items())
    try:
        fic = params["fic"]
    except:
        return render(request, "adherents/accueil_admin.html", {"msg":"Get item manquant 'fic=0 ou 1'"})

    if fic == "0":
        #filename = get_dossier_db("adherentsconf66.csv")
        filename = get_dossier_db("adherents_conf66.csv")
        #fieldnames = "NOM", "PRÉNOM", "STATUT", "ADRESSE POSTALE", "ADRESSE MAIL", "TELEPHONE", "Première ADHESION", "Somme 2023", "Type réglement 2023", "Date paiement", "PAIEMENT", "MONTANT2021", "MOYEN2021", "X", "MONTANT2022", "MOYEN2022", "Y", "Z", "2023 - somme", "2023 - moyen paiement",
        fieldnames = "NOM","PRÉNOM","STATUT","ADRESSE POSTALE","","","ADRESSE MAIL","","","TELEPHONE","ADHESION","MOYEN2020","MONTANT2020","","","MONTANT2021","MOYEN2021","","","MONTANT2022","MOYEN2022","","MONTANT2023","MOYEN2023"
    elif fic == "1":
        filename = get_dossier_db("Adhérents-Coordonnées.csv")
        fieldnames = "Nom", "Prénom", "Adresse", "Commune", "Code postal", "Téléphone", "Lien", "Mail", "Productions", "Statut", "Attestation MSA"
    elif fic == "2":
        filename = get_dossier_db("Adhérents_pcat.csv")
        fieldnames = "NOM PRENOM","STATUT(0?-1AP-2CS-3CC-4Retraite)","APE", "ADRESSE POSTALE","ADRESSE MAIL","TELEPHONE","PROFIL_PCAT","MONTANT2020","MOYEN2020","MONTANT2021","MOYEN2021","MONTANT2022","MOYEN2022","MONTANT2023","MOYEN2023"
    elif fic == "3":
        filename = get_dossier_db("adherents_pcat_2.csv")
        fieldnames = "NOM","PRENOM","GAEC","STATUT(0?-1AP-2CS-3CC-4Retraite)","APE", "ADRESSE POSTALE","CODE POSTAL","COMMUNE","ADRESSE MAIL","TELEPHONE","MONTANT2023","MOYEN2023"
    else:
        return render(request, "adherents/accueil_admin.html", {"msg":"Get item manquant 'fic=0(adherents_conf66.csv) ou 1 (Adhérents-Coordonnées.csv) ou 2 (Adhérents_pcat.csv)'"})

    msg = "import adherents_fic : " + filename
    importer_fic = True
    if importer_fic:
        with open(filename, 'r', newline='\n') as data:
            for i, line in enumerate(csv.DictReader(data, fieldnames=fieldnames, delimiter=',')):
                if i == 0:
                    continue
                if fic == "1":
                    ad = Adherent.objects.filter(Q(nom__iexact=line["Nom"], prenom__iexact=line["Prénom"]) |
                                               Q(nom__iexact=line["Nom"] + line["Prénom"])|
                                               Q(nom__iexact=line["Nom"] + " " + line["Prénom"])|
                                               Q(prenom__iexact=line["Nom"] + " " + line["Prénom"]))
                    if ad.exists():
                        for a in ad:
                            a.production_ape=line["Productions"]
                            a.adresse.rue=line["Adresse"]
                            a.adresse.code_postal=line["Code postal"]
                            a.adresse.commune=line["Commune"]
                            a.adresse.telephone=line["Téléphone"]
                            a.save()
                            msg += "<p> adherent deja present " + str(line) + str(a) + "</p>"
                        continue

                    adres = Adresse(rue=line["Adresse"], code_postal=line["Code postal"],
                                    commune=line["Commune"], telephone=line["Téléphone"])
                    adres.save()
                    adherent, created = Adherent.objects.get_or_create(nom=line["Nom"],
                             prenom=line["Prénom"],
                             statut=get_statut(line["Statut"]),
                             adresse=adres,
                             email=line["Mail"],
                             production_ape=line["Productions"],
                             asso = asso
                            )
                    msg += "<p> ajoute adherent " + str(line) + str(adherent) + "</p>"
                elif fic == "0":
                    if Adherent.objects.filter(nom=line["NOM"], prenom=line["PRÉNOM"]).exists():
                        continue

                    tel = '0' + line["TELEPHONE"][:14] if line["TELEPHONE"].startswith('6') or line["TELEPHONE"].startswith('7') else line["TELEPHONE"][:15]

                    try:
                        ad = re.split("\d{5}", line["ADRESSE POSTALE"])
                        code = re.findall("\d{5}", line["ADRESSE POSTALE"])[0]
                        adres = Adresse(rue=ad[0], code_postal=code, commune=ad[1], telephone=tel)
                    except Exception as ee:
                        msg += "<p> erreurdresse " + str(line) + str(ee) + "</p>"
                        adres = Adresse(rue=line["ADRESSE POSTALE"], telephone=tel)
                    adres.save(recalc=False)

                    adherent, created = Adherent.objects.get_or_create(nom=line["NOM"],
                            prenom=line["PRÉNOM"],
                            statut=get_statut(line["STATUT"]),
                            adresse=adres,
                            email=line["ADRESSE MAIL"]
                           )

                    if line["MONTANT2020"]:
                        adhesion, created = Adhesion.objects.get_or_create(adherent=adherent,
                                             date_cotisation='2020-01-01',
                                             montant=line["MONTANT2020"],
                                             moyen=line["MOYEN2020"],)

                    if line["MONTANT2021"]:
                         adhesion, created = Adhesion.objects.get_or_create(adherent=adherent,
                                             date_cotisation='2021-01-01',
                                             montant=line["MONTANT2021"],
                                             moyen=line["MOYEN2021"],)

                    if line["MONTANT2022"]:
                         adhesion, created = Adhesion.objects.get_or_create(adherent=adherent,
                                             date_cotisation='2022-01-01',
                                             montant=line["MONTANT2022"],
                                             moyen=line["MOYEN2022"],)

                    if line["MONTANT2023"]:
                        adhesion, created = Adhesion.objects.get_or_create(adherent=adherent,
                                            date_cotisation='2023-01-01',
                                             montant=line["MONTANT2023"],
                                             moyen=line["MOYEN2023"],)
                elif fic == "2":

                    if Adherent.objects.filter(nom=line["NOM"], prenom=line["PRÉNOM"]).exists():
                        continue

                    tel = line["TELEPHONE"][:15]

                    try:
                        ad = re.split("\d{5}", line["ADRESSE POSTALE"])
                        code = re.findall("\d{5}", line["ADRESSE POSTALE"])[0]
                        adres = Adresse(rue=ad[0], code_postal=code, commune=ad[1], telephone=tel)
                    except Exception as ee:
                        adres = Adresse(rue=line["ADRESSE POSTALE"], telephone=tel)

                    adres.save(recalc=False)
                    try :
                        profil = Profil.objects.get(username=line["PROFIL_PCAT"])
                    except:
                        profil = Profil.objects.none()

                    adherent, created = Adherent.objects.get_or_create(nom=line["NOM"],
                            prenom=line["PRÉNOM"],
                            statut=line["STATUT(0?-1AP-2CS-3CC-4Retraite)"],
                            adresse=adres,
                            profil=profil,
                            email=line["ADRESSE MAIL"]
                           )
                    for an in ["2020", "2021", "2022", "2023"]:
                        adhesion, created = Adhesion.objects.get_or_create(adherent=adherent,
                                            date_cotisation= an+'-01-01',
                                             montant=line["MONTANT"+an],
                                             moyen=line["MOYEN"+an],
                                             asso=asso)
                elif fic == "3":
                    if i >= 160:
                        continue

                    if Adherent.objects.filter(nom=line["NOM"], prenom=line["PRENOM"]).exists():
                        continue

                    if not line["CODE POSTAL"]:
                        continue

                    tel = line["TELEPHONE"][:15]

                    if Adherent.objects.filter(nom=line["NOM"] + " " + line["PRENOM"]).exists():
                        adherent = Adherent.objects.get(nom=line["NOM"] + " " + line["PRENOM"])
                        adherent.nom = line["NOM"]
                        adherent.nom_gaec=line["GAEC"],
                        adherent.prenom = line["PRENOM"]
                        adherent.statut = line["STATUT(0?-1AP-2CS-3CC-4Retraite)"]
                        adherent.email = line["ADRESSE MAIL"]
                        adherent.adresse.rue = line["ADRESSE POSTALE"]
                        adherent.adresse.commune = line["COMMUNE"]
                        adherent.adresse.code_postal = line["CODE POSTAL"]
                        adherent.adresse.save()
                        adherent.save()
                        #msg += "<p> adhrent mis à jour <a href='" + adherent.get_absolute_url()+"'>"+str(adherent)+ "</a></p>"
                    else:

                        adres, created = Adresse.objects.get_or_create(rue=line["ADRESSE POSTALE"],
                                                                           code_postal=line["CODE POSTAL"][:5],
                                                                           commune=line["COMMUNE"], telephone=tel)

                        adres.save(recalc=False)
                        adherent, created = Adherent.objects.get_or_create(nom=line["NOM"],
                                prenom=line["PRENOM"],
                                statut=line["STATUT(0?-1AP-2CS-3CC-4Retraite)"],
                                adresse=adres,
                                nom_gaec=line["GAEC"],
                               asso=asso,                             
                                email=line["ADRESSE MAIL"]
                               )
                        #msg += "<p> adhérent cree <a href='" + adherent.get_absolute_url()+"'>"+ str(adherent)+ "</a></p>"
                    for an in ["2023"]:
                        if line["MONTANT"+an]:
                            adhesion, created = Adhesion.objects.get_or_create(adherent=adherent,
                                                date_cotisation= an+'-01-01',
                                                 montant=line["MONTANT"+an],
                                                 moyen=line["MOYEN"+an],asso=asso)



    return render(request, "adherents/accueil_admin.html", {"msg":msg, "asso_slug":asso_slug})


@login_required
def getMails(request, asso_slug):
    if not is_membre_bureau(request.user, asso_slug):
        return HttpResponseForbidden()
    profils = Adherent.objects.filter(asso__slug=asso_slug)
    profils_filtres = AdherentsCarteFilter(request.GET, queryset=profils)
    return render(request, 'adherents/template_mails.html', {'qs': profils_filtres.qs, "asso_slug":asso_slug})


@login_required
def get_infos_adherent(request, asso_slug, type_info="email"):
    if not is_membre_bureau(request.user, asso_slug):
        return HttpResponseForbidden()

    profils = Adherent.objects.filter(asso__slug=asso_slug)
    profils_filtres = AdherentsCarteFilter(request.GET, queryset=profils)
    if type_info == "tel":
        template = 'adherents/template_tel.html'
    elif type_info == "email":
        template = 'adherents/template_mails.html'
    else:
        template = 'adherents/template_inconnu.html'

    return render(request, template, {'qs': profils_filtres.qs, "asso_slug":asso_slug})


@login_required
def get_infos_contacts(request, projet_pk, type_info="email"):
    projet = get_object_or_404(ProjetPhoning, pk=projet_pk)
    if not is_membre_bureau(request.user, projet.asso.slug):
        return HttpResponseForbidden()

    profils = Contact.objects.filter(projet=projet)
    profils_filtres = ContactCarteFilter(request, queryset=profils)
    if type_info == "tel":
        template = 'adherents/template_tel.html'
    elif type_info == "email":
        template = 'adherents/template_mails.html'
    else:
        template = 'adherents/template_inconnu.html'

    taille = 90
    qs = profils_filtres.qs
    if type_info == "email" and len(qs) > taille:
        data = []
        for i in range(0, len(qs), taille):
            data.append(qs[i:i + taille])
        qs = data
        return render(request, 'adherents/template_mails_groupes.html', {'qs':qs})
    return render(request, template, {'qs': profils_filtres.qs})


@login_required
def get_infos_listeMail(request, asso_slug, listeMail_pk, type_info="email"):
    liste = get_object_or_404(ListeDiffusion, pk=listeMail_pk)
    if type_info == "email":
        mails = liste.get_liste_mails
    else:
        mails = []

    return render(request, 'adherents/template_liste.html', {'liste': mails, "asso_slug":asso_slug})

@login_required
def get_infos_adherents_pasajour(request, asso_slug):
    profils = Adherent.objects.filter(asso__slug=asso_slug).order_by("nom").distinct()
    current_year = date.today().isocalendar()[0]
    mails = list(set([a.email for a in profils if not a.get_adhesion_an(current_year)]))

    return render(request, 'adherents/template_liste.html', {'liste': mails, "asso_slug":asso_slug})

@login_required
def get_infos_adherents_ajour(request, asso_slug):
    profils = Adherent.objects.filter(asso__slug=asso_slug).order_by("nom").distinct()
    current_year = date.today().isocalendar()[0]
    mails = list(set([a.email for a in profils if a.get_adhesion_an(current_year)]))

    return render(request, 'adherents/template_liste.html', {'liste': mails, "asso_slug":asso_slug})

class ListeInscriptionsMails(UserPassesTestMixin, ListView):
    model = InscriptionMail
    context_object_name = "inscriptions"
    template_name = "adherents/inscriptionMail_liste.html"
    ordering = ['liste_diffusion']

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        return self.asso

    def get_queryset(self):
        return InscriptionMail.objects.filter(liste_diffusion__asso=self.asso).order_by("-date_inscription")

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context


class InscriptionMailDetailView(UserPassesTestMixin, DetailView):
    model = InscriptionMail

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_membre_bureau'] = is_membre_bureau(self.request.user, self.asso.slug)
        context['asso_slug'] = self.asso.slug
        return context

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        return is_membre_bureau(self.request.user, self.asso.slug)

class InscriptionMailDeleteView(UserPassesTestMixin, DeleteView):
    model = InscriptionMail
    template_name_suffix = '_supprimer'

    def get_object(self):
        ad = InscriptionMail.objects.get(pk=self.kwargs['pk'])
        self.listeMail = ad.liste_diffusion
        return ad

    def get_success_url(self):
        return self.listeMail.get_absolute_url()

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        return is_membre_bureau(self.request.user, self.asso.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context

class InscriptionMailUpdateView(UserPassesTestMixin, UpdateView):
    model = InscriptionMail
    template_name_suffix = '_modifier'

    def get_form(self):
        return InscriptionMail_complet_Form(asso_slug=self.asso.slug, **self.get_form_kwargs())

    def get_success_url(self):
        return self.object.liste_diffusion.get_absolute_url()

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        return is_membre_bureau(self.request.user, self.asso.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context


class Comm_adherent_modifier(UserPassesTestMixin, UpdateView):
    model = Comm_adherent
    template_name_suffix = '_modifier'
    fields = ["commentaire"]

    def get_success_url(self):
        return self.object.adherent.get_absolute_url()

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        return is_membre_bureau(self.request.user, self.asso.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context


class Comm_adherent_supprimer(UserPassesTestMixin, DeleteView):
    model = Comm_adherent
    template_name_suffix = '_supprimer'

    def get_object(self):
        comm = Comm_adherent.objects.get(pk=self.kwargs['pk'])
        self.adherent = comm.adherent
        return comm

    def get_success_url(self):
        return self.adherent.get_absolute_url()

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        return is_membre_bureau(self.request.user, self.asso.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context

def get_mails(asso_slug, typeListe="bureau"):
    profils = Adherent.objects.filter(asso__slug=asso_slug).order_by("nom").distinct()
    current_year = date.today().isocalendar()[0]
    if typeListe=="bureau":
        return list(set([a.email for a in profils if a.profil and a.profil.estmembre_bureau_conf and a.email]))
    elif typeListe=="ajour":
        return list(set([a.email for a in profils if a.get_adhesion_an(current_year).montant and a.email]))
    elif typeListe=="anneeprecedente_pasajour":
        return list(set([a.email for a in profils if a.get_adhesion_an(current_year-1).montant and not a.get_adhesion_an(current_year).montant and a.email]))
    elif typeListe=="pasajour":
        return list(set([a.email for a in profils if not a.get_adhesion_an(current_year).montant and a.email]))


class ListeDiffusion_liste(UserPassesTestMixin, ListView, ):
    model = ListeDiffusion
    context_object_name = "listesDiffusion"
    template_name = "adherents/listediffusion_list.html"
    ordering = ['nom']


    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        self.request.session["asso_slug"] = self.asso.slug
        return self.request.user.isCotisationAJour(self.asso.slug) or self.request.user.is_superuser

    def get_queryset(self):
        return ListeDiffusion.objects.filter(asso=self.asso).order_by("nom")

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        context['actions'] = Action.objects.filter(verb__startswith="listeDiff_"+self.asso.slug).order_by('-timestamp')
        context['dico_ListesBase'] = {'Bureau': get_mails(typeListe="bureau"),
                                        'Adhérents à jour':get_mails(typeListe="ajour"),
                                        "Adhérents de l'année dernière pas à jour de cotisation":get_mails(typeListe="anneeprecedente_pasajour"),
                                        'Adhérents (depuis 2021) pas à jour de cotisation':get_mails(typeListe="pasajour")}
        context['is_membre_bureau'] = self.request.user.estmembre_bureau(self.asso.slug)

        return context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context


class ListeDiffusionDetailView(UserPassesTestMixin, DetailView):
    model = ListeDiffusion
    ordering = ['nom']

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        return self.request.user.isCotisationAJour(self.asso.slug) or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        context['is_membre_bureau'] = self.request.user.estmembre_bureau(self.asso.slug)
        return context


class ListeDiffusionDeleteView(UserPassesTestMixin, DeleteView):
    model = ListeDiffusion
    template_name_suffix = '_supprimer'

    def get_success_url(self):
        return self.adherent.get_absolute_url()

    def get_object(self):
        ad = Adhesion.objects.get(pk=self.kwargs['pk'])
        self.adherent = ad.adherent
        return ad

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        return is_membre_bureau(self.request.user, self.asso.slug)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context

class ListeDiffusionUpdateView(UserPassesTestMixin, UpdateView):
    model = ListeDiffusion
    template_name_suffix = '_modifier'
    fields = ["nom"]

    def get_success_url(self):
        return self.object.adherent.get_absolute_url()

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        return is_membre_bureau(self.request.user, self.asso.slug)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context

@login_required
def creerInscriptionMail_adherent(request, asso_slug, adherent_pk):
    if not is_membre_bureau(request.user, asso_slug):
        return HttpResponseForbidden()

    adherent = get_object_or_404(Adherent, pk=adherent_pk)
    form = InscriptionMailAdherentALsteForm(request.POST or None)
    if form.is_valid():
        inscription = form.save(commit=False)
        inscription.adherent = adherent
        inscription.save()
        action.send(inscription.adherent, verb="listeDiff_"+asso.slug+"_plus", action_object=inscription.liste_diffusion, url=inscription.liste_diffusion.get_absolute_url(),
                     description=" ajouté dans la liste: '%s'" %(inscription.liste_diffusion.nom))
        return redirect(reverse('adherents:inscriptionMail_liste', kwargs={"asso_slug":asso_slug} ))

    return render(request, 'adherents/inscriptionmail_ajouter.html', {"form": form, 'adherent':adherent})


@login_required
def creerInscriptionMail(request, asso_slug):
    if not is_membre_bureau(request.user, asso_slug):
        return HttpResponseForbidden()

    form = InscriptionMail_listeAdherent_Form(asso_slug, request.POST or None)
    if form.is_valid():
        inscription = form.save()
        action.send(inscription.adherent, verb="listeDiff_"+asso_slug+"_plus", action_object=inscription.liste_diffusion, url=inscription.liste_diffusion.get_absolute_url(),
                     description=" ajouté dans la liste: '%s'" %(inscription.liste_diffusion.nom))
        return redirect(reverse('adherents:inscriptionMail_liste', kwargs = {"asso_slug":asso_slug}))

    return render(request, 'adherents/inscriptionmail_ajouter.html', {"form": form})

@login_required
def creerListeDiffusion(request, asso_slug):
    asso = testIsMembreAsso(request, asso_slug)
    if not is_membre_bureau(request.user, asso_slug):
        return HttpResponseForbidden()

    form = ListeDiffusionForm(request.POST or None)
    if form.is_valid():
        liste = form.save(commit = False)
        liste.asso = asso
        liste.save()
        action.send(request.user, verb="listeDiff_"+asso_slug+"_nouvelle", action_object=liste, url=liste.get_absolute_url(),
                     description="a créé une nouvelle liste : '%s'" %(liste.nom))
        return redirect(liste)

    return render(request, 'adherents/listediffusion_ajouter.html', {"form": form})


@login_required
def ajouter_comm_adh(request, asso_slug, adherent_pk):
    if not is_membre_bureau(request.user, asso_slug):
        return HttpResponseForbidden()
    adherent = get_object_or_404(Adherent, pk=adherent_pk)
    form = Comm_adh_form(request.POST or None)
    if form.is_valid():
        comm = form.save(commit=False)
        comm.adherent = adherent
        comm.save()
        return redirect(comm.adherent)

    return render(request, 'adherents/comm_adh_ajouter.html', {"form": form, "asso_slug":asso_slug})


@login_required
def ajouterInscription_AdherentListeDiffusion(request, asso_slug, listeMail_pk, adherent_pk):
    testIsMembreAsso(request, asso_slug,)

    listeMail = get_object_or_404(ListeDiffusion, pk=listeMail_pk)
    adherent = get_object_or_404(Adherent, pk=adherent_pk)
    InscriptionMail.objects.create(liste_diffusion=listeMail,
                                   date_inscription=now(),
                                   adherent=adherent)

    return redirect(reverse('adherents:listeMail', asso_slug=asso_slug))


@login_required
def mesListesMails(request, asso_slug):
    asso = testIsMembreAsso(request, asso_slug)
    if not Adherent.objects.filter(profil=request.user, asso=asso).exists():
        return render(request, 'adherents/profil_inconnu.html', {"asso_slug":asso_slug})
    adherent = Adherent.objects.get(profil=request.user, asso=asso)
    liste = []
    for listeMail in ListeDiffusion.objects.filter(asso=asso):
        if InscriptionMail.objects.filter(liste_diffusion=listeMail, adherent=adherent).exists():
            liste.append([listeMail, "inscrit", adherent.pk])
        else:
            liste.append([listeMail, "pasinscrit", adherent.pk])

    return render(request, 'adherents/listediffusion_mesListes.html', {'liste_inscriptions': liste, 'adherent':adherent, 'asso_slug':asso_slug})


@login_required
def swap_inscription(request, asso_slug, listeMail_pk, adherent_pk):
    listeMail = get_object_or_404(ListeDiffusion, pk=listeMail_pk)
    adherent = get_object_or_404(Adherent, pk=adherent_pk)
    inscrit = InscriptionMail.objects.filter(liste_diffusion=listeMail,
                                   adherent=adherent)
    if inscrit:
        inscrit.delete()
        action.send(adherent, verb="listeDiff_"+asso_slug+"_moins", action_object=listeMail, url=listeMail.get_absolute_url(),
                     description=request.user.username + " a retiré %s de la liste : '%s'" %(adherent, listeMail.nom))
    else:
        InscriptionMail.objects.create(liste_diffusion=listeMail, adherent=adherent).save()
        action.send(adherent, verb="listeDiff_"+asso_slug+"_plus", action_object=listeMail, url=listeMail.get_absolute_url(),
                     description=request.user.username + " a ajouté %s dans la liste : '%s'" %(adherent, listeMail.nom))

    return redirect('adherents:mesListesMails', asso_slug=asso_slug)


@login_required
def ajouterAdherentAListeDiffusion(request, asso_slug, listeDiffusion_pk):
    if not is_membre_bureau(request.user, asso_slug):
        return HttpResponseForbidden()

    form = InscriptionMailForm(asso_slug, request.POST or None)
    listeDiffusion = get_object_or_404(ListeDiffusion, pk=listeDiffusion_pk)

    if form.is_valid():
        adhesion = form.save(commit=False)
        adhesion.liste_diffusion = listeDiffusion
        adhesion = form.save()
        action.send(adhesion.adherent, verb="listeDiff_"+asso_slug+"_plus", action_object=listeDiffusion, url=listeDiffusion.get_absolute_url(),
                     description=request.user.username + " a ajouté %s dans la liste : '%s'" %(adhesion.adherent, listeDiffusion.nom))

        return redirect(listeDiffusion)

    return render(request, 'adherents/listediffusion_ajouterAdherent.html', {"form": form, 'liste': listeDiffusion, "asso_slug":asso_slug})



@login_required
def ajouterMailAListeDiffusion(request, asso_slug, listeDiffusion_pk):
    if not is_membre_bureau(request.user, asso_slug):
        return HttpResponseForbidden()

    form = InscriptionMail_Mail_Form(request.POST or None)
    listeDiffusion = get_object_or_404(ListeDiffusion, pk=listeDiffusion_pk)

    if form.is_valid():
        adhesion = form.save(commit=False)
        adhesion.liste_diffusion = listeDiffusion
        adhesion = form.save()
        action.send(adhesion, verb="listeDiff_"+asso_slug+"_plus", action_object=listeDiffusion, url=listeDiffusion.get_absolute_url(),
                     description=request.user.username + " a ajouté %s dans la liste : '%s'" %(adhesion.get_email, listeDiffusion.nom))

        return redirect(listeDiffusion)

    return render(request, 'adherents/listediffusion_ajouterAdherent.html', {"form": form, 'liste': listeDiffusion, "asso_slug":asso_slug})
