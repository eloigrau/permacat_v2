from bourseLibre.views_base import DeleteAccess
from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponseRedirect
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView
from django.http import HttpResponseForbidden
from django.urls import reverse_lazy
from bourseLibre.models import Asso
from bourseLibre.views import testIsMembreAsso
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from .forms import ReunionForm, ReunionChangeForm, ParticipantReunionForm, PrixMaxForm, \
    ParticipantReunionMultipleChoiceForm, ParticipantReunionChoiceForm, Distance_ParticipantReunionForm, \
    ChoixAdherentConf, NoteDeFrais_form, NoteDeFrais_update_form
from .models import Reunion, ParticipantReunion, Choix, get_typereunion, Distance_ParticipantReunion, NoteDeFrais, \
    ChoixMoyenPaiement
from bourseLibre.forms import AdresseForm, AdresseForm3, AdresseForm4
from datetime import datetime
from django.contrib.auth.mixins import UserPassesTestMixin
import itertools
import csv
from django.http import HttpResponse

@login_required
def lireReunion(request, slug):
    reunion = get_object_or_404(Reunion, slug=slug)
    request.session['reunion_courante_url'] = reunion.get_absolute_url()
    request.session['asso_slug'] = reunion.asso.slug
    if not reunion.est_autorise(request.user):
        return render(request, 'notMembre.html', {"asso": str(reunion.asso)})

    liste_participants = [(x, x.getDistance_route_allerretour(reunion), x.get_url(reunion), x.get_gmaps_url(reunion), x.getDistance_objet(reunion)) for x in reunion.participants.all()]

    context = {'reunion': reunion, 'liste_participants': liste_participants}

    return render(request, 'defraiement/lireReunion.html', context,)


@login_required
def recalculerDistanceReunion(request, slug_reunion):
    reunion = get_object_or_404(Reunion, slug=slug_reunion)
    reunion.recalculerDistance()
    return redirect(reverse('defraiement:lireReunion', kwargs={"slug": slug_reunion}))


@login_required
def lireParticipant(request, id):
    part = get_object_or_404(ParticipantReunion, id=id)
    reunions = part.reunion_set.all().order_by('-start_time')
    reu = [(r, part.getDistance_route_allerretour(r)) for r in reunions]
    context = {"part":part, 'reunions': reu}

    return render(request, 'defraiement/lireParticipant.html', context,)

def getRecapitulatif_km(request, reunions, asso, export=False):
    participants = ParticipantReunion.objects.filter(asso=asso)
    if export:
        entete = ["nom", ] + [r.titre+ " (" + str(r.start_time) + ")"  for r in reunions] + ["total Euros",]
    else:
        entete = ["nom", ] + ["<a href="+r.get_absolute_url()+">" +r.titre+"</a>" + " (" + str(r.start_time) + ")" for r in reunions] + ["km parcourus",]
    lignes = []
    lignes.append([""] + [r.get_categorie_display() for r in reunions] + ["", ])
    for p in participants:
        distances = [round(p.getDistance_route_allerretour(r), 2) if p in r.participants.all() else 0 for r in reunions ]
        if sum(distances) > 0:
            if export:
                part = [p.nom, ] + distances + [sum(distances), ]
            else:
                part = ["<a href=" + p.get_absolute_url() + ">" +p.nom+"</a>", ] + distances + [round(sum(distances), 2) , ]
            lignes.append(part)
    distancesTotales = [round(r.getDistanceTotale, 2) for r in reunions]
    lignes.append(["Total", ] + distancesTotales + [round(sum(distancesTotales), 2), ])
    return entete, lignes

def getRecapitulatif_euros(request, reunions, asso, prixMax, tarifKilometrique, export=False):
    participants = ParticipantReunion.objects.filter(asso=asso)
    if export:
        entete = ["nom", ] + [r.titre for r in reunions] + ["total Euros",]
    else:
        entete = ["nom", ] + ["<a href="+r.get_absolute_url()+">" + r.titre+"</a>" + " (" + str(r.start_time) + ")" for r in reunions] + ["total Euros",]
    lignes = []

    lignes.append([""] + [r.get_categorie_display() for r in reunions] + ["Total", ])
    distancesTotales = [r.getDistanceTotale for r in reunions]
    prixTotal = sum(distancesTotales) * float(tarifKilometrique)
    if prixTotal < float(prixMax):
        coef_distanceTotale = float(tarifKilometrique)
    else:
        coef_distanceTotale = float(prixMax) / sum(distancesTotales)
    for p in participants:
        distances = [int(p.getDistance_route_allerretour(r) * coef_distanceTotale + 0.5) if p in r.participants.all() else 0 for r in reunions ]
        if sum(distances) > 0:
            if export:
                part = [p.nom, ] + distances + [sum(distances), ]
            else:
                part = ["<a href=" + p.get_absolute_url() + ">" +p.nom+"</a>", ] + distances + [sum(distances), ]
            lignes.append(part)
    distancesTotales = [int(r.getDistanceTotale * coef_distanceTotale + 0.5) for r in reunions]
    lignes.append(["Total", ] + distancesTotales + [sum(distancesTotales), ])
    lignes.append(["prix max : " + str(prixMax), "bareme kilometrique max : " + str(tarifKilometrique),
                   "barème calculé : " + str(round(coef_distanceTotale, 3)), ] + ["" for r in reunions[2:]] + ["", ])

    return entete, lignes

@login_required
def recapitulatif(request, asso_slug):
    asso = testIsMembreAsso(request, asso_slug)
    if not isinstance(asso, Asso):
        raise PermissionDenied
    type_reunion = request.GET.get('type_reunion')
    if type_reunion:
        reunions = Reunion.objects.filter(estArchive=False, asso=asso, categorie=type_reunion, ).order_by('categorie','start_time',)
    else:
        type_reunion = "999"
        reunions = Reunion.objects.filter(estArchive=False, asso=asso, ).order_by('start_time','categorie',).order_by('categorie','start_time',)

    annee = request.GET.get('annee')
    if annee:
        reunions = reunions.filter(start_time__year=annee)
    else:
        reunions = reunions.filter(start_time__year=datetime.now().year)

    entete, lignes = getRecapitulatif_km(request, reunions, asso)
    asso_list = [(x.nom, x.slug) for x in Asso.objects.all().order_by("id")
                            if request.user.est_autorise(x.slug)]
    type_list = get_typereunion(asso_slug)
    form = PrixMaxForm(request.POST or None)
    if form.is_valid():
        prixMax = form.cleaned_data["prixMax"]
        tarifKilometrique = form.cleaned_data["tarifKilometrique"]
        entete, lignes = getRecapitulatif_euros(request, reunions, asso, prixMax, tarifKilometrique)

        return render(request, 'defraiement/recapitulatif.html', {"form": form, "entete":entete, "lignes":lignes, "unite":"euros", "asso_list":asso_list, "type_list":type_list, "type_courant":type_reunion, "prixMax":prixMax, "tarifKilometrique":tarifKilometrique})

    return render(request, 'defraiement/recapitulatif.html', {"form": form, "asso":asso, "entete":entete, "lignes":lignes, "unite":"km", "asso_list":asso_list, "type_list":type_list, "type_courant":type_reunion, "prixMax":"", "tarifKilometrique":""},)


def export_recapitulatif(request, asso, type_reunion="999", type_export="km",):
    asso = testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied

    prixMax = request.GET.get('prixMax', 100000)
    tarifKilometrique = request.GET.get('tarifKilometrique', 1)

    if type_reunion != "999":
        reunions = Reunion.objects.filter(estArchive=False, asso=asso, categorie=type_reunion).order_by('start_time','categorie',)
    else:
        reunions = Reunion.objects.filter(estArchive=False, asso=asso, ).order_by('start_time','categorie',)

    annee = request.GET.get('annee', False)
    if annee:
        reunions = reunions.filter(start_time__year=annee)
    else:
        annee = now().year
        reunions = reunions.filter(start_time__year=annee)

    if type_export == "km":
        entete, lignes = getRecapitulatif_km(request, reunions, asso, export=True)
        csv_data = [entete, ] + lignes
    else:
        entete, lignes = getRecapitulatif_euros(request, reunions, asso, prixMax, tarifKilometrique, export=True)
        csv_data = [entete, ] + lignes

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    return StreamingHttpResponse(
        (writer.writerow(row) for row in csv_data),
        content_type="text/csv",
        )
    return response



@login_required
def export_participants(request, asso):
    asso = testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied

    participants = ParticipantReunion.objects.filter(asso=asso).order_by("nom")

    lignes = [["nom", "date", "catégorie", "réunion", "code postal", "commune", "km(total)"], ]

    annee = request.GET.get('annee', now().year)
    for p in participants:
        for r in p.reunion_set.filter(start_time__year=annee).order_by('start_time'):
            lignes.append([p.nom, r.start_time, r.get_categorie_display(), r.titre, r.adresse.code_postal, r.adresse.commune, p.getDistance_route_allerretour(r)])

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    return StreamingHttpResponse(
            (writer.writerow(row) for row in lignes),
            content_type="text/csv",
        )
    return response

@login_required
def export_UnParticipant(request, asso, participant_id):
    asso = testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied

    participant = ParticipantReunion.objects.get(id=participant_id, asso=asso)

    lignes = [["nom", "date", "catégorie", "réunion", "code postal", "commune", "km(total)"], ]

    annee = request.GET.get('annee', now().year)
    for r in participant.reunion_set.filter(start_time__year=annee).order_by('start_time'):
        lignes.append([participant.nom, r.start_time, r.get_categorie_display(), r.titre, r.adresse.code_postal, r.adresse.commune, participant.getDistance_route_allerretour(r)])

    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    return StreamingHttpResponse(
            (writer.writerow(row) for row in lignes),
            content_type="text/csv",
        )
    return response
@login_required
def ajouterReunion(request, asso_slug):
    form = ReunionForm(asso_slug, request.POST or None)
    request.session["asso_slug"] = asso_slug

    if form.is_valid():
        reu = form.save(request.user)
        reu.asso = Asso.objects.get(slug=asso_slug)
        reu.save()
        return redirect(reverse('defraiement:ajouterAdresseReunion', kwargs={"slug": reu.slug}))

    return render(request, 'defraiement/ajouterReunion.html', { "form": form})


@login_required
def modifierParticipantReunion(request, id):
    part = ParticipantReunion.objects.get(id=id)
    form = ParticipantReunionForm(request.POST or None, part.nom)
    form_adresse = AdresseForm3(request.POST or None, instance=part.adresse)

    if form.is_valid() and form_adresse.is_valid():
        adresse = form_adresse.save()
        part.nom = form.cleaned_data['nom']
        part.adresse = adresse
        part.save()
        return redirect(part.get_absolute_url())

    return render(request, 'defraiement/modifierParticipantReunion.html', {'part':part, 'form':form,'form_adresse':form_adresse})

# @login_required
class ModifierParticipant(UpdateView):
    model = ParticipantReunion
    template_name_suffix = '_modifier'
    success_url = reverse_lazy('defraiement:participants')

    def get_object(self):
        return ParticipantReunion.objects.get(id=self.kwargs['id'])

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.object.get_success_url())

# @login_required
class ModifierReunion(UpdateView):
    model = Reunion
    form_class = ReunionChangeForm
    template_name_suffix = '_modifier'

    def form_valid(self, form):
        self.object = form.save()
        self.object.date_modification = now()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_form(self,*args, **kwargs):
        form = super(ModifierReunion, self).get_form(*args, **kwargs)
        form.fields["asso"].choices = [(x.id, x.nom) for i, x in enumerate(Asso.objects.all().order_by('nom')) if self.request.user.estMembre_str(x.slug)]
        return form

def ajouterAdresseReunion(request, slug):
    reunion = get_object_or_404(Reunion, slug=slug)
    form_adresse = AdresseForm4(request.POST or None)

    if form_adresse.is_valid():
        adresse = form_adresse.save()
        reunion.adresse = adresse
        reunion.save()
        return redirect(reunion)

    return render(request, 'defraiement/ajouterAdresseReunion.html', {'reunion':reunion, 'form_adresse2':form_adresse })

def ajouterAdresseReunionChezParticipant(request, slug):
    reunion = get_object_or_404(Reunion, slug=slug)
    form = ParticipantReunionChoiceForm(reunion.asso.slug, request.POST or None)

    if form.is_valid():
        reunion.adresse = form.cleaned_data["participant"].adresse
        reunion.save()
        return redirect(reunion)

    return render(request, 'defraiement/ajouterAdresseReunionFromParticpant.html', {'reunion':reunion, 'form':form })

def modifierAdresseReunion(request, slug):
    reunion = get_object_or_404(Reunion, slug=slug)
    #form_adresse = AdresseForm(request.POST or None, instance=reunion)
    form_adresse = AdresseForm4(request.POST or None)

    if form_adresse.is_valid():#form_adresse.is_valid() or
        # if 'adressebtn' in request.POST:
        #     adresse = form_adresse.save()
        # else:
        adresse = form_adresse.save()
        reunion.adresse = adresse
        reunion.save()
        return redirect(reunion)

    return render(request, 'defraiement/modifierAdresseReunion.html', {'reunion':reunion, 'form_adresse':form_adresse }) # 'form_adresse':form_adresse,

class SupprimerParticipant(DeleteAccess, DeleteView, UserPassesTestMixin):
    model = ParticipantReunion
    success_url = reverse_lazy('defraiement:participants')
    template_name_suffix = '_supprimer'

    def test_func(self):
        return self.request.user.is_superuser

    def get_object(self):
        self.asso_abrev = self.kwargs['asso_abrev']
        return ParticipantReunion.objects.get(id=self.kwargs['id'])

    def get_success_url(self):
        return reverse('defraiement:participants', kwargs={'asso_slug':self.asso_abrev})

class SupprimerReunion(DeleteAccess, DeleteView):
    model = Reunion
    success_url = reverse_lazy('defraiement:reunions')
    template_name_suffix = '_supprimer'

    def get_object(self):
        reu = Reunion.objects.get(slug=self.kwargs['slug'])
        self.asso = reu.asso
        return Reunion.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self):
        return reverse('defraiement:reunions_asso', kwargs={'asso_slug':self.asso.slug})

@login_required
def ajouterParticipant(request, asso_slug):
    asso = testIsMembreAsso(request, asso_slug)
    form = ParticipantReunionForm(request.POST or None, )
    form_adresse2 = AdresseForm4(request.POST or None)
    if form.is_valid() and form_adresse2.is_valid():
        adresse = form_adresse2.save()
        part = form.save(adresse, asso)
        try:
            return redirect(request.session.get('reunion_courante_url'))
        except:
            return redirect('defraiement:participants', asso_slug=asso_slug)


    return render(request, 'defraiement/ajouterParticipant.html', {'form': form,'form_adresse2':form_adresse2 }) # 'form_adresse':form_adresse,


@login_required
def ajouterParticipantAsso(request, asso_slug):
    form = ChoixAdherentConf(request.POST or None, )
    if form.is_valid():
        adherent = form.cleaned_data["adherent"]
        part = ParticipantReunion.objects.create(
            asso=Asso.objects.get(slug=asso_slug),
            nom=adherent.nom + " " + adherent.prenom,
            adresse=adherent.adresse)
        url = request.session.get('reunion_courante_url', part.get_absolute_url())
        return redirect(url)

    if asso_slug=='conf66':
        return render(request, 'defraiement/ajouterParticipantConf.html', {'form': form }) # 'form_adresse':form_adresse,
    return render(request, 'defraiement/ajouterParticipant.html', {'form': form }) # 'form_adresse':form_adresse,


@login_required
def ajouterParticipantReunion(request, slug_reunion):
    reunion = get_object_or_404(Reunion, slug=slug_reunion)
    asso = reunion.asso
    form = ParticipantReunionForm(request.POST or None, )
    form_choice = ParticipantReunionChoiceForm(asso.slug, request.POST or None)
    form_adresse2 = AdresseForm3(request.POST or None)

    if form_choice.is_valid() or (form.is_valid() and form_adresse2.is_valid()):#(form_adresse.is_valid() or form_adresse2.is_valid()):
        if form_choice.is_valid():
            if form_choice.cleaned_data and form_choice.cleaned_data["participant"]:
                reunion.participants.add(form_choice.cleaned_data["participant"])
                reunion.save()
                return redirect(reunion)
        adresse = form_adresse2.save()
        participant = form.save(adresse, asso)

        reunion.participants.add(participant)
        reunion.save()
        return redirect(reunion)

    return render(request, 'defraiement/ajouterParticipantReunion.html', {'reunion':reunion, 'form': form, 'form_choice':form_choice,  'form_adresse2':form_adresse2, }) ##'form_adresse':form_adresse,


@login_required
def ajouterParticipantsReunion(request, slug_reunion):
    reunion = get_object_or_404(Reunion, slug=slug_reunion)
    asso = reunion.asso
    form_choice = ParticipantReunionMultipleChoiceForm(asso.slug, request.POST or None)

    if form_choice.is_valid():
        for p in form_choice.cleaned_data["participants"]:
            reunion.participants.add(p)
        reunion.save()
        return redirect(reunion)

    return render(request, 'defraiement/ajouterParticipantsReunion.html', {'reunion':reunion, 'form_choice':form_choice }) ##'form_adresse':form_adresse,


@login_required
def ajouterAdresseReunion(request, slug):
    reunion = Reunion.objects.get(slug=slug)
    #form_adresse = AdresseForm(request.POST or None)
    form_adresse = AdresseForm4(request.POST or None)

    if form_adresse.is_valid(): #form_adresse.is_valid() or
        # if 'adressebtn' in request.POST:
        #     adresse = form_adresse.save()
        # else:
        adresse = form_adresse.save()
        reunion.adresse = adresse
        reunion.save()
        return redirect(reunion)

    return render(request, 'defraiement/ajouterAdresseReunion.html', {'reunion':reunion, 'form_adresse':form_adresse }) #'form_adresse':form_adresse,


def supprimerParticipantReunion(request, slug_reunion, id_participantReunion):
    reu = Reunion.objects.get(slug=slug_reunion)
    parti = reu.participants.get(id=id_participantReunion)
    reu.participants.remove(parti)
    return redirect(reu)

#
# class SupprimerParticipantReunion(DeleteView):
#     model = ParticipantReunion
#     success_url = reverse_lazy('defraiement:reunions')
#     template_name_suffix = '_supprimer'
#
#     def get_object(self):
#         return
#     def delete(self, request, *args, **kwargs):
#         parti = self.get_object()
#         return redirect(self.get_success_url())
#
#     def get_success_url(self):
#         return
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         context['reunion'] = Reunion.objects.get(slug=self.kwargs['slug_reunion'])
#         return context

@login_required
def voirLieux(request,):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation de voir les lieux")
    titre = "tous les lieux"
    lieux = Reunion.objects.filter().order_by('titre')

    return render(request, 'defraiement/carte_touslieux.html', {'titre':titre, "lieux":lieux})


#
# class ListeReunions(ListView):
#     model = Reunion
#     context_object_name = "reunion_list"
#     template_name = "defraiement/reunion_list.html"
#     paginate_by = 100
#
#     def get_queryset(self):
#         params = dict(self.request.GET.items())
#         qs = Reunion.objects.filter(estArchive=False)
#
#         if "annee" in params:
#             qs = qs.filter(start_time__year = params['annee'])
#
#         if "categorie" in params:
#             qs = qs.filter(categorie=params['categorie'])
#
#         if "ordreTri" in params:
#             qs = qs.order_by(params['ordreTri'])
#         else:
#             qs = qs.order_by('-start_time', 'categorie', 'titre', )
#
#         return qs
#
#     def get_context_data(self, **kwargs):
#         # Call the base implementation first to get a context
#         context = super().get_context_data(**kwargs)
#         context['list_archive'] = Reunion.objects.filter(estArchive=True)
#
#         cat= Reunion.objects.order_by('categorie').values_list('categorie', flat=True).distinct()
#         context['categorie_list'] = [x for x in Choix.type_reunion if x[0] in cat]
#         context['ordreTriPossibles'] = ['-date_creation', 'categorie', 'titre' ]
#
#         if 'categorie' in self.request.GET:
#             context['typeFiltre'] = "categorie"
#             context['categorie_courante'] = [x[1] for x in Choix.type_reunion if x[0] == self.request.GET['categorie']][0]
#         if 'ordreTri' in self.request.GET:
#             context['typeFiltre'] = "ordreTri"
#         context['asso_courante'] = "Public"
#         return context


class ListeReunions_asso(ListView):
    model = Reunion
    context_object_name = "reunion_list"
    template_name = "reunions/reunion_list.html"
    paginate_by = 100

    def get_queryset(self):
        self.params = dict(self.request.GET.items())
        self.asso = Asso.objects.get(slug=self.kwargs['asso_slug'])
        qs = Reunion.objects.filter(estArchive=False, asso=self.asso)

        if "annee" in self.params:
            qs = qs.filter(start_time__year=self.params['annee'])
        else:
            qs = qs.filter(start_time__year=datetime.now().year)

        if "categorie" in self.params:
            qs = qs.filter(categorie=self.params['categorie'])

        if "ordreTri" in self.params:
            qs = qs.order_by(self.params['ordreTri'])
        else:
            qs = qs.order_by('-start_time', 'categorie', 'titre', )

        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        self.request.session["asso_slug"] = self.asso.slug

        self.asso = Asso.objects.get(slug=self.kwargs['asso_slug'])
        reu = Reunion.objects.filter(estArchive=False, asso=self.asso)
        cat = reu.values_list('categorie', flat=True).distinct()
        context['categorie_list'] = [x for x in Choix.type_reunion if x[0] in cat]
        context['ordreTriPossibles'] = Choix.ordre_tri_reunions
        context['type_courant'] = self.params["categorie"] if "categorie" in self.params else ""

        return context

@login_required
def carte_reunions(request, asso_slug, ):
    asso = testIsMembreAsso(request, asso_slug)
    qs = Reunion.objects.filter(estArchive=False, asso=asso)
    params = dict(request.GET.items())
    request.session["asso_slug"] = asso_slug
    if "annee" in params:
        qs = qs.filter(start_time__year=params['annee'])
    else:
        qs = qs.filter(start_time__year=datetime.now().year)

    return render(request, 'defraiement/carte_reunions.html', {'reunions':qs, })


class ListeParticipants(ListView):
    model = ParticipantReunion
    context_object_name = "participant_list"
    template_name = "reunions/participantreunion_list.html"
    paginate_by = 30

    def get_queryset(self):
        self.asso = Asso.objects.get(slug=self.kwargs['asso_slug'])
        self.request.session["asso_slug"] = self.asso.slug
        qs = ParticipantReunion.objects.filter(asso=self.asso).order_by("nom")
        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        #context['list_archive'] = Reunion.objects.filter(estArchive=True, asso=self.asso)
        context['asso_courante'] = self.asso
        return context


@login_required
def lireReunion_id(request, id):
    atelier = get_object_or_404(Reunion, id=id)
    return lireReunion(request, atelier)



class ModifierDistance_ParticipantReunion(UpdateView):
    model = Distance_ParticipantReunion
    form = Distance_ParticipantReunionForm
    template_name_suffix = '_modifier'
    fields = ['type_trajet', 'distance', 'contexte_distance',]

#
# from django.http import HttpResponse
# from django.template import Context, Template
# from django.views.decorators.csrf import csrf_exempt
# from .forms import FormForm
#
# @csrf_exempt
# def pageTest(request):
#     form = FormForm()
#     if request.method == 'POST':
#         form = FormForm(request.POST)
#
#     t = Template("""<form method="post" action=".">{{f}}<input type="submit"><form>""")
#     c = {'f': form.as_p()}
#     return HttpResponse(t.render(Context(c)))




import csv

from django.http import StreamingHttpResponse

class Echo:
    """An object that implements just the write method of the file-like
    interface.
    """
    def write(self, value):
        """Write the value by returning it, instead of storing in a buffer."""
        return value

#
# def get_csv(request):
#     """A view that streams a large CSV file."""
#
#     recap = getRecapitulatif_km()
#     csv_data = [
#         ("NOM PRENOM","STATUT","APE", "ADRESSE POSTALE","ADRESSE MAIL","TELEPHONE","MONTANT2020","MOYEN2020","MONTANT2021","MOYEN2021","MONTANT2022","MOYEN2022","MONTANT2023","MOYEN2023"),]
#     csv_data += [(a.nom +" "+ a.prenom, a.statut, a.production_ape,a.adresse.code_postal+ " " + a.adresse.commune,  a.email, a.adresse.telephone, a.get_adhesion_an(2020).montant,
#           a.get_adhesion_an(2020).montant, a.get_adhesion_an(2021).montant, a.get_adhesion_an(2021).montant, a.get_adhesion_an(2022).montant, a.get_adhesion_an(2022).montant, a.get_adhesion_an(2023).montant, a.get_adhesion_an(2023).montant) for a in Adherent.objects.all() ]


class NoteDeFrais_ajouter(UserPassesTestMixin, CreateView, ):
    model = NoteDeFrais
    template_name = 'defraiement/ndf_ajouter.html'

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])

        return self.asso.est_autorise(self.request.user) or self.request.user == self.object.profil

    def get_form(self):
        return NoteDeFrais_form(self.asso.slug, **self.get_form_kwargs())

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.auteur = self.request.user
        self.object.asso = self.asso
        self.object.save()
        return redirect(self.object.get_absolute_url())


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context

class NoteDeFrais_detail(UserPassesTestMixin, DetailView):
    model = NoteDeFrais
    template_name = 'defraiement/ndf_detail.html'

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.request.session['asso_slug'])
        return self.asso.est_autorise(self.request.user) or self.request.user == self.object.profil

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class NoteDeFrais_modifier(UserPassesTestMixin, UpdateView, ):
    model = NoteDeFrais
    template_name = 'defraiement/ndf_modifier.html'
    form_class = NoteDeFrais_update_form

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.request.session['asso_slug'])
        return self.asso.est_autorise(self.request.user) or self.request.user == self.object.profil

    def get_object(self):
        return NoteDeFrais.objects.get(pk=self.kwargs['pk'])

    def get_form_kwargs(self):
        kwargs = super(NoteDeFrais_modifier, self).get_form_kwargs()
        kwargs.update({'asso_slug': self.asso.slug})
        return kwargs

    def form_valid(self, form):
        self.object = form.save()
        if "next" in self.request.GET:
            return redirect(self.request.GET["next"])
        return redirect(self.get_success_url())

    def get_success_url(self):
        return self.object.get_absolute_url()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context

class NoteDeFrais_supprimer(UserPassesTestMixin, DeleteView, ):
    model = NoteDeFrais
    template_name_suffix = '_supprimer'

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.request.session['asso_slug'])
        return self.asso.est_autorise(self.request.user) or self.request.user == self.object.profil

    def get_success_url(self):
        return reverse('defraiement:ndf_list', kwargs={'asso_slug': self.asso.slug})


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context



class ListeNdf_asso(UserPassesTestMixin, ListView):
    model = NoteDeFrais
    context_object_name = "ndf_list"
    template_name = "defraiement/ndf_list.html"
    paginate_by = 100

    def test_func(self):
        self.asso = testIsMembreAsso(self.request, self.kwargs['asso_slug'])
        self.request.session['asso_slug'] = self.asso.slug
        return self.asso.est_autorise(self.request.user)

    def get_queryset(self):
        self.params = dict(self.request.GET.items())
        self.asso = Asso.objects.get(slug=self.kwargs['asso_slug'])
        self.request.session["asso_slug"] = self.asso.slug
        qs = NoteDeFrais.objects.filter(estArchive=False, asso=self.asso)

        if "annee" in self.params:
            qs = qs.filter(date_note__year=self.params['annee'])
        else:
            qs = qs.filter(date_note__year=datetime.now().year)

        if "categorie" in self.params:
            qs = qs.filter(categorie=self.params['categorie'])

        if "ordreTri" in self.params:
            qs = qs.order_by(self.params['ordreTri'])
        else:
            qs = qs.order_by('-date_note', 'categorie', 'titre', )

        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        self.request.session["asso_slug"] = self.asso.slug

        context['ndf_list_archive'] = NoteDeFrais.objects.filter(estArchive=True, asso=self.asso)
        cat = context['ndf_list_archive'].values_list('categorie', flat=True).distinct()
        context['categorie_list'] = [x for x in ChoixMoyenPaiement.choices if x[0] in cat]
        context['ordreTriPossibles'] = Choix.ordre_tri_ndf
        context['type_courant'] = self.params["categorie"] if "categorie" in self.params else ""

        return context
