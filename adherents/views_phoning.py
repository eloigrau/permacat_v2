
from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView

from django.shortcuts import get_object_or_404, HttpResponseRedirect
import csv
from django.db.models import Q
from .forms import (Paysan_form, Paysan_update_form, ContactPaysan_form,
                    ListeTel_form, csvFile_form, csvText_form)

from .models import Adherent, Paysan, ContactPaysan
from bourseLibre.models import Adresse, Profil, Asso
from .filters import AdherentsCarteFilter, PaysanCarteFilter
from actstream.models import Action
from datetime import date, timedelta, datetime

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from actstream import actions, action
from io import StringIO
from django.db.models import Count, Max
import re

class Paysan_ajouter(CreateView):
    model = Paysan
    template_name_suffix = '_ajouter'

    def get_form(self):
        return Paysan_form(**self.get_form_kwargs())

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.adresse=Adresse.objects.create(rue=form.cleaned_data['rue'],
                                                   commune=form.cleaned_data['commune'],
                                                   code_postal=form.cleaned_data['code_postal'],
                                                   telephone=form.cleaned_data['telephone'])

        self.object.save()
        #action.send(self.request.user, verb='jardins_nouveau_jp', action_object=self.object, url=self.object.get_absolute_url(),
        #             description="a ajouté le Jardin: '%s'" % self.object.titre)

        return redirect("adherents:accueil_phoning")



class Paysan_modifier(UpdateView):
    model = Paysan
    template_name_suffix = '_modifier'

    def get_form(self):
        return Paysan_update_form(**self.get_form_kwargs())

    def get_initial(self):
        paysan = Paysan.objects.get(pk=self.kwargs["pk"])
        return {
            'rue': paysan.adresse.rue,
            'commune': paysan.adresse.commune,
            'code_postal': paysan.adresse.code_postal,
            'telephone': paysan.adresse.telephone,
        }

    def form_valid(self, form):
        self.object = form.save()
        self.object.adresse.rue=form.cleaned_data['rue']
        self.object.adresse.commune=form.cleaned_data['commune']
        self.object.adresse.code_postal=form.cleaned_data['code_postal']
        self.object.adresse.telephone=form.cleaned_data['telephone']
        self.object.adresse.save(recalc=True)
        #action.send(self.request.user, verb='jardins_nouveau_jp', action_object=self.object, url=self.object.get_absolute_url(),
        #             description="a ajouté le Jardin: '%s'" % self.object.titre)

        return redirect("adherents:accueil_phoning")
    # def form_valid(self, form):
    #     desc = " a modifié l'adhérent : " + str(self.object.nom) + ", " + str(self.object.prenom)+ " (" + str(
    #         form.changed_data) + ")"
    #     action.send(self.request.user, verb='adherent_conf66_modifier', action_object=self.object,
    #                 url=self.object.get_absolute_url(), description=desc)
    #     titre = "[PCAT_adherents] Modification de l'adherent : " + str(self.object)
    #     action.send(self.request.user, verb='emails', url=self.object.get_absolute_url(), titre=titre, message=str(self.request.user) + desc, emails=['confederationpaysanne66@gmail.com', ])
    #     return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


class Paysan_supprimer(UserPassesTestMixin, DeleteView):
    model = Paysan
    template_name_suffix = '_supprimer'

    def test_func(self):
        return True

    def get_success_url(self):
        #desc = " a supprimé l'adhérent : " + str(self.object.nom) + ", " + str(self.object.prenom)
        #action.send(self.request.user, verb='adherent_conf66_supprimer', url=reverse('adherents:accueil'), description=desc)
        return reverse('adherents:accueil_phoning')


@login_required
def paysan_supprimer(request, paysan_pk):
    paysan = get_object_or_404(Paysan, pk=paysan_pk)
    paysan.delete()
    return redirect('adherents:accueil_phoning')

class Paysan_liste(ListView):
    model = Paysan
    context_object_name = "paysans"
    template_name = "adherents/carte_paysans.html"
    template_name_simple = "adherents/carte_paysans_simple.html"

    def get_queryset(self):
        params = dict(self.request.GET.items())
        #self.asso = Asso.objects.get(abreviation=self.kwargs['asso_slug'])
        if "lettre" in self.request.GET:
            qs = Paysan.objects.filter(nom__istartswith=self.request.GET["lettre"]).order_by("nom","prenom","email","adresse__telephone")
        else:
            qs = Paysan.objects.all().order_by("nom","prenom","email","adresse__telephone")
        profils_filtres = PaysanCarteFilter(self.request.GET, queryset=qs)
        self.qs = profils_filtres.qs.distinct()
        return self.qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        context['titre'] = "Phoning Conf pour APCA 2024 (%d)" % len(qs)
        filter = AdherentsCarteFilter(self.request.GET, qs)
        context["filter"] = filter
        #context['is_membre_bureau'] = is_membre_bureau(self.request.user)
        context['historique'] = Action.objects.filter(Q(verb__startswith='phoningConf_'))
        return context

    def get_template_names(self, *args, **kwargs):
        # Check if the request path is the path for a-url in example app
        if self.request.path == reverse('adherents:accueil_phoning_simple'):
            return [self.template_name_simple]  # Return a list that contains "a.html" template name
        return [self.template_name]  # else return "b.html" template name




@login_required
def contactPaysan_supprimer(request, paysan_contact_pk):
    c = get_object_or_404(ContactPaysan, pk=paysan_contact_pk)
    c.delete()
    return redirect('adherents:accueil_phoning')

@login_required
def contactPaysan_ajouter(request, paysan_pk):
    p = get_object_or_404(Paysan, pk=paysan_pk)
    form = ContactPaysan_form(request.POST or None)
    if form.is_valid():
        contact = form.save(commit=False)
        contact.paysan = p
        form.save(commit=True)
        return redirect('adherents:accueil_phoning')

    return render(request, 'adherents/paysan_contact_ajouter.html', {"form": form, "paysan":p})



@login_required
def paysan_ajouter_accueil(request):
    return render(request, 'adherents/paysan_ajouter_acceuil.html', {})


@login_required
def nettoyer_telephones(request):
    m = ""
    for p in Paysan.objects.all():
        if p.adresse.rue:
            try:
                ad = re.split("\d{5}", p.adresse.rue)
                if len(ad>1):
                    code = re.findall("\d{5}", p.adresse.rue)[0]
                    p.adresse.rue = ad[0]
                    p.adresse.code_postal=code
                    p.adresse.commune=ad[1]
                    p.adresse.save()
                    m+= "<p>MAJ " + p.adresse.rue + "</p>"
            except:
                m+= "<p>pb " + p.adresse.rue + "</p>"
        if p.adresse.telephone:
            if p.adresse.telephone.startswith("6"):
                p.adresse.telephone = "0" + str(p.adresse.telephone)
                p.adresse.save()
                m += "<p>ajustement6 tel : " + str(p.adresse.telephone) + "</p>"
                continue
            if p.adresse.telephone.startswith("7"):
                p.adresse.telephone = "0" + str(p.adresse.telephone)
                p.adresse.save()
                m += "<p>ajustement7 tel : " + str(p.adresse.telephone) + "</p>"
                continue

            if len(p.adresse.telephone) < 4:
                p.commentaire = p.commentaire if p.commentaire else "" + " " + str(p.adresse.telephone)
                p.adresse.telephone = ""
                p.adresse.save()
                m += "<p>petit tel : " + str(p.adresse.telephone) + "</p>"
                continue

            try:
                v = int(p.adresse.telephone)
            except:

                p.commentaire = p.commentaire if p.commentaire else "" + " " + str(p.adresse.telephone)
                p.adresse.telephone = ""
                p.adresse.save()
                m += "<p>deplacement tel : " + str(p.adresse.telephone) + "</p>"

    return render(request, 'adherents/paysan_ajouter_listetel_res.html', {"message": m})


@login_required
def supprimer_doublons(request):
    params = dict(request.GET.items())
    if 'tel' in params:
        unique_fields = ['adresse__telephone', ]
    else:
        unique_fields = ['nom', 'prenom', 'adresse__telephone']

    duplicates = (
        Paysan.objects.values(*unique_fields)
        .order_by('nom')
        .annotate(max_id=Max('id'), count_id=Count('id'))
        .filter(count_id__gt=1)
    )

    for duplicate in duplicates:
        (
            Paysan.objects
            .filter(**{x: duplicate[x] for x in unique_fields})
            .exclude(id=duplicate['max_id'])
            .delete()
        )


    return redirect('adherents:accueil_phoning')


@login_required
def creerPaysan(telephone, nom=None, prenom=None, email=None, rue=None, commune=None, code_postal=None, adherent=None):
    if not telephone:
        return 0, None
    if not Paysan.objects.filter(adresse__telephone=telephone).exists():
        adresse, created = Adresse.objects.get_or_create(
                                        telephone=telephone,
                                        commune=commune,
                                        code_postal=code_postal,
                                        rue=rue,
                                        )
        p, created = Paysan.objects.get_or_create(
                                nom=nom,
                                prenom=prenom,
                                email=email,
                                adherent=adherent,
                                adresse=adresse,
        )
        return 1, p
    return 0, None


@login_required
def ajouterAdherentsConf(request):
    adherents = Adherent.objects.all()
    m = ""
    for adherent in adherents:
        res, p = creerPaysan(adherent.nom, adherent.prenom,adherent.email, adherent.adresse.telephone, adherent.adresse.rue,
                    adherent.adresse.commune, adherent.adresse.code_postal, adherent)
        if res:
            m += "<p>ajout " + str(adherent) +"</p>"
        else:
            m += "<p>refus " + str(adherent) +"</p>"


    return render(request, 'adherents/paysan_ajouter_listetel_res.html', {"message": m})



@login_required
def phoning_paysan_ajouter_listetel(request):
    form = ListeTel_form(request.POST or None)
    if form.is_valid():
        tels = form.cleaned_data['telephones']
        m = ""
        for i, tel in enumerate(tels.split(',')):
            if len(tel)<5:
                m += "<p>" + str(i) +" Errlong " + str(tel) +" > " + "</p>"
                continue
            try:
                res, p = creerPaysan(telephone=str(tel))
                if res:
                    m += "<p>" + str(i) +" ajout " + str(p) +"</p>"
                else:
                    m += "<p>" + str(i) +" refus " + str(tel) +"</p>"
            except Exception as e:
                m += "<p>" + str(i) +" erreur " + str(tel) +" > " + str(e) + "</p>"

        return render(request, 'adherents/paysan_ajouter_listetel_res.html', {"liste_tel": tels, "message": m})

    return render(request, 'adherents/paysan_ajouter_listetel.html', {"form": form})


def lireTableauPaysan(csv_reader):
    msg = ""
    for i, line in enumerate(csv_reader):
        #if i == 0:
        #    continue
        try:
            cles = line.keys()
            if line["telephone"] and Adresse.objects.filter(telephone__iexact=line["telephone"]):
                msg += "<p> DEJA " + str(line) + "#" + line["telephone"] +"#</p>"
                continue
            if not line["telephone"] :
                msg += "<p> pas de tel " + str(line) + "</p>"
            #    continue
            adres, created = Adresse.objects.get_or_create(rue=line["rue"] if 'rue' in cles  else "",
                                                           code_postal=line["code_postal"] if 'code_postal' in cles else "",
                                                           commune=line["commune"]  if 'commune' in cles  else "",
                                                           telephone=line["telephone"])
            adres.save()
            paysan, created = Paysan.objects.get_or_create(
                nom=line["nom"] if 'nom' in cles else "",
                prenom=line["prenom"] if 'prenom' in cles else "",
                adresse=adres,
                email=line["email"] if 'email' in cles else "",
            )
            if created:
                msg += "<p> ajoute adherent " + str(line) + " / " + str(paysan) + "</p>"
            else:
                msg += "<p>  adherent  deja present " + str(line) + " / " + str(paysan) + "</p>"

        except Exception as e:
            msg += "<p>Erreur " + str(e.__traceback__) + " > " + str(i) + " " + str(line)
    return msg


@login_required
def phoning_paysan_ajouter_csv(request):
    form = csvText_form(request.POST or None)
    if form.is_valid():
        texte_csv = form.cleaned_data['texte_csv']
        msg = "import texte_csv : "
        csv_reader = csv.DictReader(StringIO(texte_csv))
        if not "telephone" in csv_reader.fieldnames:
            return render(request, 'adherents/paysan_ajouter_listetel_res.html', {"liste_tel": str(csv_reader.fieldnames), "message": m})

        m = lireTableauPaysan(csv_reader)
        return render(request, 'adherents/paysan_ajouter_listetel_res.html', {"liste_tel": str(csv_reader), "message": m})

    return render(request, 'adherents/paysan_ajouter_csv1.html', {"form": form})



@login_required
def phoning_paysan_ajouter_csv2(request):
    form = csvFile_form(request.POST or None, request.FILE or None)
    if form.is_valid():
        fichier = request.FILES['fichier_csv']
        msg = "import adherents_fic : " + fichier
        with open(fichier, 'r', newline='\n') as data:
            csv_reader = csv.DictReader(data, delimiter=',')
            if not "telephone" in csv_reader.fieldnames:
                return render(request, 'adherents/paysan_ajouter_listetel_res.html', {"liste_tel": str(csv_reader.fieldnames), "message": m})

            m = lireTableauPaysan(csv_reader)
        return render(request, 'adherents/paysan_ajouter_listetel_res.html', {"liste_tel": str(csv_reader), "message": m})

    return render(request, 'adherents/paysan_ajouter_csv2.html', {"form": form})



@login_required
def import_adherents_ggl(request):
    params = dict(request.GET.items())
    # fic = params["fic"]


    return render(request, "adherents/accueil_admin.html", {"msg":msg})

