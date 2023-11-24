import re

from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, HttpResponseRedirect
import csv
from django.db.models import Q
from bourseLibre.settings import PROJECT_ROOT, os
from bourseLibre.settings.production import LOCALL
from .forms import AdhesionForm, AdherentForm
from .models import Adherent, Adhesion
from bourseLibre.models import Adresse
from .filters import AdherentsCarteFilter
# Create your views here.


@login_required
def accueil_admin(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    return render(request, "adherents/accueil_admin.html", {'msg':"Tout est pret"})


class ListeAdherents(ListView):
    model = Adherent
    context_object_name = "adherents"
    template_name = "adherents/carte_adherents.html"

    def get_queryset(self):
        params = dict(self.request.GET.items())
        if "lettre" in self.request.GET:
            qs = Adherent.objects.filter(nom__istartswith=self.request.GET["lettre"]).order_by("nom")
        else:
            qs = Adherent.objects.all().order_by("nom")
        profils_filtres = AdherentsCarteFilter(self.request.GET, queryset=qs)
        self.qs = profils_filtres.qs
        return profils_filtres.qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['titre'] = "Adhérents Conf 66"
        return context


def get_dossier_db(nomfichier):
    if LOCALL:
        return "/home/tchenrezi/Téléchargements/" + nomfichier
    return os.path.abspath(os.path.join(PROJECT_ROOT, "../../", nomfichier))

@login_required
def modif_APE(request):
    if not request.user.adherent_conf66:
        return HttpResponseForbidden()
    msg = ""
    for a in Adherent.objects.filter(production_ape__isnull=False):
        old = str(a.production_ape)
        if len(str(a.production_ape).split("PE "))>1:
            a.production_ape = str(a.production_ape).split("PE ")[1]
            a.save()
            msg += str(a.production_ape) + " from " + old + "\n"
    return render(request, "adherents/accueil_admin.html", {'msg':"Tout est pret"})



@login_required
def import_adherents_ggl(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    params = dict(request.GET.items())
    try:
        fic = params["fic"]
    except:
        return render(request, "adherents/accueil_admin.html", {"msg":"Get item manquant 'fic=0 ou 1'"})

    if fic == "0":
        filename = get_dossier_db("adherentsconf66.csv")
        fieldnames = "NOM", "PRÉNOM", "STATUT", "ADRESSE POSTALE", "ADRESSE MAIL", "TELEPHONE", "Première ADHESION", "Somme 2023", "Type réglement 2023", "Date paiement", "PAIEMENT", "MONTANT2021", "MOYEN2021", "X", "MONTANT2022", "MOYEN2022", "Y", "Z", "2023 - somme", "2023 - moyen paiement",
    elif fic == "1":
        filename = get_dossier_db("Adhérents-Coordonnées.csv")
        fieldnames = "Nom", "Prénom", "Adresse", "Commune", "Code postal", "Téléphone", "Lien", "Mail", "Productions", "Statut", "Attestation MSA"
    else:
        return render(request, "adherents/accueil_admin.html", {"msg":"Get item manquant 'fic=0 ou 1'"})

    msg = "import adherents_fic : " + filename
    importer_fic = True
    if importer_fic:
        with open(filename, 'r', newline='\n') as data:
            for i, line in enumerate(csv.DictReader(data, fieldnames=fieldnames, delimiter=',')):
                if i == 0:
                    continue
                if i >= 150:
                    break
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
                            msg += "<p> adherent deja present " + str(line) + str(ad) + "</p>"
                        continue

                    adres = Adresse(rue=line["Adresse"], code_postal=line["Code postal"],
                                    commune=line["Commune"], telephone=line["Téléphone"])
                    adres.save()
                    adherent, created = Adherent.objects.get_or_create(nom=line["Nom"],
                             prenom=line["Prénom"],
                             statut=line["Statut"],
                             adresse=adres,
                             email=line["Mail"],
                             production_ape=line["Productions"],
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
                            statut=line["STATUT"],
                            adresse=adres,
                            email=line["ADRESSE MAIL"]
                           )

                    if line["Somme 2023"]:
                        adhesion, created = Adhesion.objects.get_or_create(adherent=adherent,
                                             date_cotisation='2023-01-01',
                                             montant=line["Somme 2023"],
                                             moyen=line["Type réglement 2023"],)

                    if line["2023 - somme"]:
                         adhesion, created = Adhesion.objects.get_or_create(adherent=adherent,
                                             date_cotisation='2023-01-01',
                                             montant=line["2023 - somme"],
                                             moyen=line["2023 - moyen paiement"],)

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
    return render(request, "adherents/accueil_admin.html", {"msg":msg})



class AdherentDetailView(DetailView):
    model = Adherent
    template_name_suffix = '_detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['adhesions'] = Adhesion.objects.filter(adherent=self.object)
        return context

class AdherentDeleteView(DeleteView):
    model = Adherent
    template_name_suffix = '_supprimer'


    def get_success_url(self):
        return reverse('adherents:accueil')


class AdherentUpdateView(UpdateView):
    model = Adherent
    template_name_suffix = '_modifier'
    fields = ["nom", "prenom", "statut", "email"]

class AdherentAdresseUpdateView(UpdateView):
    model = Adresse
    template_name_suffix = '_modifier'
    fields = ["rue", "code_postal", "commune", "latitude", "longitude", "telephone"]

def adherent_ajouter(request):
    if not request.user.adherent_conf66:
        return HttpResponseForbidden()

    form = AdherentForm(request.POST or None)
    if form.is_valid():
        adresse = Adresse.objects.create(
            rue=form.cleaned_data['rue'],
            code_postal=form.cleaned_data['code_postal'],
            telephone=form.cleaned_data['telephone'],
            latitude=form.cleaned_data['latitude'],
            longitude=form.cleaned_data['longitude'],
        )
        adherent = form.save(commit=False)
        adherent.adresse = adresse
        adherent = form.save()
        return redirect(adherent)

    return render(request, 'adherents/adherent_ajouter.html', {"form": form})



class ListeAdhesions(ListView):
    model = Adhesion
    context_object_name = "adhesions"
    template_name = "adherents/adhesion_liste.html"

    #def get_queryset(self):
    #    params = dict(self.request.GET.items())

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        return context


class AdhesionDetailView(DetailView):
    model = Adhesion

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class AdhesionDeleteView(DeleteView):
    model = Adhesion
    template_name_suffix = '_supprimer'

    def get_success_url(self):
        return self.adherent.get_absolute_url()

    def get_object(self):
        ad = Adhesion.objects.get(pk=self.kwargs['pk'])
        self.adherent = ad.adherent
        return ad

class AdhesionUpdateView(UpdateView):
    model = Adhesion
    template_name_suffix = '_modifier'
    fields = ["date_cotisation", "montant", "moyen", "detail"]

    def get_success_url(self):
        return self.object.adherent.get_absolute_url()


def ajouterAdhesion(request, adherent_pk):
    if not request.user.adherent_conf66:
        return HttpResponseForbidden()

    form = AdhesionForm(request.POST or None)
    adherent = get_object_or_404(Adherent, pk=adherent_pk)
    if form.is_valid():
        adhesion = form.save(commit=False)
        adhesion.adherent = adherent
        adhesion = form.save()
        return redirect(adherent)

    return render(request, 'adherents/adhesion_ajouter.html', {"form": form, 'adherent': adherent})
