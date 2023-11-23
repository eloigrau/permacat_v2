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
    return render(request, "adherents/accueil_admin.html", {'msg':"Tout est pret"})


class ListeAdherents(ListView):
    model = Adherent
    context_object_name = "adherents"
    template_name = "adherents/carte_adherents.html"

    def get_queryset(self):
        params = dict(self.request.GET.items())
        if "lettre" in self.request.GET:
            qs = Adherent.objects.filter(nom__istartswith=self.request.GET["lettre"])
        else:
            qs = Adherent.objects.all()
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
def import_adherents_ggl(request):
    filename = get_dossier_db("adherentsconf66.csv")
    msg = "import adherents_fic : " + filename
    importer_fic = True
    fieldnames = "NOM","PRÉNOM","STATUT","ADRESSE POSTALE","ADRESSE MAIL","TELEPHONE","Première ADHESION","Somme 2023","Type réglement 2023","Date paiement","PAIEMENT","MONTANT2021","MOYEN2021","X","MONTANT2022","MOYEN2022","Y","Z","2023 - somme","2023 - moyen paiement",
    if importer_fic:
        with open(filename, 'r', newline='\n') as data:
            csvreader = csv.DictReader(data, fieldnames=fieldnames, delimiter=',')
            header = next(csvreader)
            for line in csvreader:
                try:
                    tel = '0' + line["TELEPHONE"] if line["TELEPHONE"].startswith('6') or line["TELEPHONE"].startswith('7') else line["TELEPHONE"]

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
                            mail=line["ADRESSE MAIL"]
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
                except Exception as e:
                    msg += "<p> erreur " + str(line) + str(e) + "</p>"

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

class AdherentUpdateView(UpdateView):
    model = Adherent
    template_name_suffix = '_modifier'
    fields = ["nom", "prenom", "statut", "email"]

class AdherentAdresseUpdateView(UpdateView):
    model = Adresse
    template_name_suffix = '_modifier'
    fields = ["rue", "code_postal", "commune", "latitude", "longitude", "telephone"]

def adherent_ajouter(request):
    if not request.user.is_superuser:
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

    #def get_object(self):
    #    return Adhesion.objects.get(slug=self.kwargs['slug'])

class AdhesionUpdateView(UpdateView):
    model = Adhesion
    template_name_suffix = '_modifier'
    fields = ["date_cotisation", "montant", "moyen", "detail"]



def ajouterAdhesion(request, adherent_pk):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    form = AdhesionForm(request.POST or None)
    adherent = get_object_or_404(Adherent, pk=adherent_pk)
    if form.is_valid():
        form.save()
        return redirect(adherent)

    return render(request, 'adherents/adhesion_ajouter.html', {"form": form, 'adherent': adherent})
