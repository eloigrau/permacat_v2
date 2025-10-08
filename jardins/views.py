from django.shortcuts import render, redirect, reverse
from django.core.exceptions import PermissionDenied
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, HttpResponseRedirect
import csv
from django.db.models import Q
from bourseLibre.settings import PROJECT_ROOT, os
from bourseLibre.filters import ProfilCarteFilter
from bourseLibre.settings.production import LOCALL
from bourseLibre.forms import AdresseForm4
from bourseLibre.models import Asso, Profil, Salon
from .forms import Plante_rechercheForm, GrainothequeForm, GrainothequeChangeForm, JardinForm, JardinChangeForm, \
    GraineForm, InfoGraineForm, ContactParticipantsForm, SalonJardinForm, PlanteDeJardinForm, InfoPlanteForm, \
    ChoisirMonJardinForm, ChoisirMaGrainothequeForm
from .models import Plante, Jardin, Grainotheque, Graine, InscriptionJardin, PlanteDeJardin, InfoPlante, \
    DBStatut_inpn, DBRang_inpn, DBHabitat_inpn, DBVern_inpn, DB_importeur, InfoGraine, GenericModel, RTG_import
from .filters import JardinCarteFilter, GrainoCarteFilter
from actstream import actions, action
from webpush import send_user_notification
from dal import autocomplete
from bs4 import BeautifulSoup
from bourseLibre.settings.production import SERVER_EMAIL
from bourseLibre.views_admin import send_mass_html_mail
from hitcount.models import HitCount
from hitcount.views import HitCountMixin

def accueil(request):
    obj, created = GenericModel.objects.get_or_create(type_article='Jardins et Grainothèques', message="")
    hit_count = HitCount.objects.get_for_object(obj)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    return render(request, "jardins/accueil.html", {'msg':"Tout est pret"})

@login_required
def accueil_admin(request):
    return render(request, "jardins/accueil_admin.html", {'msg':"Tout est pret"})


def get_dossier_db(nomfichier):
    if LOCALL:
        return "/home/tchenrezi/Téléchargements/bdd_rtg/" + nomfichier

    #return os.path.abspath(os.path.join(PROJECT_ROOT, "../../../", nomfichier))
    return os.path.abspath(os.path.join(PROJECT_ROOT, "../static/jardins/", nomfichier))

@login_required
def import_db_inpn_0(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    msg =" impor plantes "
    filename = get_dossier_db("TAXREFv16_plante.txt")
    if 'reset' in request.GET:
        Plante.objects.all().delete()
    if 'j_max' in request.GET:
        j_max = int(request.GET["j_max"])
    else:
        j_max = 200000
    if 'j_min' in request.GET:
        j_min = int(request.GET["j_min"])
    else:
        j_min = 0

    j = 0
    k = 0
    dbg, created = DB_importeur.objects.get_or_create(nom='db_taxref')
    dbg.lg_debut = int(dbg.lg_fin)
    msg +=" j_min" + str(j_min) + " jmax" + str(j_max)
    with open(filename, 'r') as data:
        for i, line in enumerate(csv.DictReader(data, delimiter="\t")):
            if i > j_max:
                break
            if i < j_min or i < dbg.lg_debut:
                continue
            if line["REGNE"] and line["NOM_VERN"] and (line["RANG"] == "ES" or line["RANG"] == "GN" or line["RANG"] == "SC") \
                    and (line["REGNE"] == "Plantae"):
                if Plante.objects.filter(CD_NOM=line["CD_NOM"]).exists():
                    continue

                if Plante.objects.filter(LB_NOM=line["LB_NOM"]).exists():
                    p = Plante.objects.get(LB_NOM=line["LB_NOM"])
                    if not p.infos_supp:
                        p.infos_supp = line["URL"] + "; "
                    elif line["CD_NOM"] not in p.infos_supp:
                        p.infos_supp = p.infos_supp + line["URL"] + "; "
                    p.save()
                    k += 1
                elif Plante.objects.filter(NOM_VERN=line["NOM_VERN"]).exists() :
                    p = Plante.objects.get(NOM_VERN=line["NOM_VERN"])
                    if not p.infos_supp:
                        p.infos_supp = line["URL"] + "; "
                    elif line["CD_NOM"] not in p.infos_supp:
                        p.infos_supp = p.infos_supp + line["URL"] + "; "
                    p.save()
                    k += 1
                else:
                    try:
                        if not line["CD_SUP"]:
                            line["CD_SUP"] = 0
                        Plante(**line).save()
                        j += 1
                    except Exception as e:
                        msg += "<p> erreur " + str(line) + str(e) + "</p>"
            if i % 1000 == 0:
                dbg.lg_fin = i
                dbg.save()
    msg += "<p>j total" + str(j) + " k :" +str(k) + "</p>"
    if dbg.texte:
        dbg.texte = dbg.texte + msg
    else:
        dbg.texte = msg
    dbg.save()

    return render(request, "jardins/accueil.html", {"msg":msg})

@login_required
def import_db_inpn_1(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    try:
        msg = "import rang OK"
        filename = get_dossier_db("rangs_note.csv")
        DBRang_inpn.objects.all().delete()
        with open(filename, 'r', encoding='latin-1' ) as data:
            for i, line in enumerate(csv.DictReader(data, delimiter=';')):
                if not DBRang_inpn.objects.filter(RG_LEVEL=line["RG_LEVEL"]).exists():
                    DBRang_inpn(**line).save()
    except Exception as e:
            msg += "<p>" + str(e) + "</p>"

    return render(request, "jardins/accueil.html", {"msg":msg})




@login_required
def import_db_inpn_2(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    try:
        msg = "import statut OK"
        filename = get_dossier_db("statuts_note.csv")
        DBStatut_inpn.objects.all().delete()
        with open(filename, 'r', encoding='iso-8859-1' ) as data:
            for i, line in enumerate(csv.DictReader(data, delimiter=';')):
                if not DBStatut_inpn.objects.filter(ORDRE=line["ORDRE"]).exists():
                    DBStatut_inpn(**line).save()

    except Exception as e:
            msg += "<p>" + str(e) + "</p>"

    return render(request, "jardins/accueil.html", {"msg":msg})

@login_required
def import_db_inpn_3(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    try:
        msg = "import habitat OK"
        filename = get_dossier_db("habitats_note.csv")
        DBHabitat_inpn.objects.all().delete()
        with open(filename, 'r', encoding='iso-8859-1' ) as data:
            for i, line in enumerate(csv.DictReader(data, delimiter=';')):
                if not DBHabitat_inpn.objects.filter(HABITAT=line["HABITAT"]).exists():
                    DBHabitat_inpn(**line).save()
    except Exception as e:
            msg += "<p>" + str(e) + "</p>"
    return render(request, "jardins/accueil.html", {"msg":msg})

@login_required
def import_db_inpn_4(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    try:
        msg = "import vern OK"
        filename = get_dossier_db("TAXVERNv16.txt")
        DBVern_inpn.objects.all().delete()
        with open(filename, 'r', ) as data:
            for i, line in enumerate(csv.DictReader(data, delimiter='\t')):
                if not DBVern_inpn.objects.filter(CD_VERN=line["CD_VERN"]).exists():
                    DBVern_inpn(**line).save()
    except Exception as e:
            msg += "<p>" + str(e) + "</p>"

    return render(request, "jardins/accueil.html", {"msg":"import vern OK"})

@login_required
def import_grainotheque_rtg_1(request):
    filename = get_dossier_db("inventaireRTG1.csv")
    msg = "import rtg1 OK"
    importer_fic = True
    fieldnames = 'maj_lettre', 'nom', 'famille', 'genre', 'espece', 'annee', 'stock', 'lieu_recolte', 'observations'
    if importer_fic:
        grainotheque, cree = Grainotheque.objects.get_or_create(slug='ramene-ta-graine')
        InfoGraine.objects.all().delete()
        Graine.objects.filter(grainotheque__pk=grainotheque.pk).delete()
        RTG_import.objects.all().delete()
        with open(filename, 'r', newline='\n') as data:
            for line in csv.DictReader(data, fieldnames=fieldnames, delimiter=','):
                try:
                    if len(line["nom"]) > 4 and not RTG_import.objects.filter(nom=line["nom"], annee=line["annee"], observations=line["observations"],lieu_recolte=line["lieu_recolte"],).exists():
                        ligne = RTG_import(**line).save()
                        plantess = ligne.get_plante_bdd()
                        infos = ligne.get_InfoGraine()
                        if not Graine.objects.filter(nom=ligne.nom, grainotheque__pk=grainotheque.pk,infos__description=infos.description).exists():
                            if len(plantess) > 0:
                                g = Graine(nom=ligne.nom, grainotheque=grainotheque, plante=plantess[0], infos=infos)
                            else:
                                g = Graine(nom=ligne.nom, grainotheque=grainotheque, infos=infos)
                            g.save()
                        else:
                            msg += "<p>deja present" + str(ligne.nom)+ " "+ str(line) + "</p>"

                except Exception as e:
                    msg += "<p>" + str(e) + "//" + str(line)+ "</p>"
            data.close()
    return render(request, "jardins/accueil_admin.html", {"msg":msg})

@login_required
def import_grainotheque_rtg_2(request):
    filename = get_dossier_db("inventaireRTG2.csv")
    msg = "import rtg2 OK"
    importer_fic = True
    fieldnames = 'maj_lettre', 'nom', 'famille', 'genre', 'espece', 'annee', 'stock', 'lieu_recolte', 'observations'
    if importer_fic:
        grainotheque, cree = Grainotheque.objects.get_or_create(slug='ramene-ta-graine')
        with open(filename, 'r', newline='\n') as data:
            for line in csv.DictReader(data, fieldnames=fieldnames, delimiter=','):
                try:
                    if len(line["nom"]) > 4 and not RTG_import.objects.filter(nom=line["nom"], annee=line["annee"], observations=line["observations"],lieu_recolte=line["lieu_recolte"],).exists():
                        ligne = RTG_import(**line).save()
                        plantess = ligne.get_plante_bdd()
                        infos = ligne.get_InfoGraine()
                        if not Graine.objects.filter(nom=ligne.nom, grainotheque__pk=grainotheque.pk,infos__description=infos.description).exists():
                            if len(plantess) > 0:
                                g = Graine(nom=ligne.nom, grainotheque=grainotheque, plante=plantess[0], infos=infos)
                            else:
                                g = Graine(nom=ligne.nom, grainotheque=grainotheque, infos=infos)
                            g.save()
                        else:
                            msg += "<p>deja present" + str(ligne.nom)+ " "+ str(line) + "</p>"
                except Exception as e:
                    msg += "<p>" + str(e) + "//" + str(line)+ "</p>"
            data.close()
    return render(request, "jardins/accueil_admin.html", {"msg":msg})



@login_required
def import_grainotheque_rtg_3(request):
    grainotheque, cree = Grainotheque.objects.get_or_create(slug='ramene-ta-graine')

    msg = "import rtg ("+ str(len(RTG_import.objects.all())) + ")"

    #InfoGraine.objects.all(graine__grainotheque__pk=grainotheque.pk).delete()
    InfoGraine.objects.all().delete()
    Graine.objects.filter(grainotheque__pk=grainotheque.pk).delete()

    for ligne in RTG_import.objects.all():
        #try:
        plantess = ligne.get_plante_bdd()
        infos = ligne.get_InfoGraine()
        if not Graine.objects.filter(nom=ligne.nom, grainotheque__pk=grainotheque.pk,infos__description=infos.description).exists():
            if len(plantess) > 0:
                g = Graine(nom=ligne.nom, grainotheque=grainotheque, plante=plantess[0], infos=infos)
            else:
                g = Graine(nom=ligne.nom, grainotheque=grainotheque, infos=infos)
            g.save()

       # except Exception as e:
        #msg += "<p>("+str(ligne)+ str(plantess) + "</p>"

    return render(request, "jardins/accueil_admin.html", {"msg":msg})

class ListePlantes(ListView):
    model = Plante
    context_object_name = "plantes_list"
    template_name = "jardins/plantes.html"

    def get_queryset(self):
        params = dict(self.request.GET.items())

        self.qs = Plante.objects.none()
        if "recherche" in params:
            self.qs = Plante.objects.filter(Q(RANG="ES") & (Q(NOM_VERN__icontains=params['recherche']) | Q(NOM_COMPLET__icontains=params['recherche'])| Q(LB_NOM__icontains=params['recherche'])))

            if 'lettre' in params:
                self.qs = self.qs.filter(NOM_VERN__istartswith=params['lettre'])
        elif 'lettre' in params:
            self.qs = Plante.objects.filter(RANG="ES", NOM_VERN__istartswith=params['lettre'])

        if "categorie" in params:
            self.qs = self.qs.filter(categorie=params['categorie'])

        if "plante" in params:
            return redirect("jardins:voir_plante", cd_nom=str(params["plante"]))

        if self.qs.count() == 1:
            return redirect("jardins:voir_plante", cd_nom=str(self.qs[0].CD_NOM))

        if "ordreTri" in params:
            self.qs = self.qs.order_by(params['ordreTri'])
        else:
            self.qs = self.qs.order_by('NOM_VERN', )


        return self.qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['plantesDesJardins'] = PlanteDeJardin.objects.filter(Q(jardin__visibilite_annuaire="0") | Q(jardin__visibilite_annuaire="1"))
        else:
            context['plantesDesJardins'] = PlanteDeJardin.objects.filter(jardin__visibilite_annuaire="0")

        if "recherche" in self.request.GET:
            context['recherche'] = self.request.GET["recherche"]
        else:
            context['recherche'] = "Trouver une plante..."
        if 'categorie' in self.request.GET:
            context['typeFiltre'] = "categorie"
           # context['categorie_courante'] = [x[1] for x in Choix.type_atelier if x[0] == self.request.GET['categorie']][0]
        if 'ordreTri' in self.request.GET:
            context['typeFiltre'] = "ordreTri"

        context['plant_form'] = Plante_rechercheForm(None)

        return context

def voir_plante(request, cd_nom):
    try:
        p = Plante.objects.get(CD_NOM=int(cd_nom))
    except:
        return render(request, "jardins/plante.html", {"msg":"plante introuvable (" + str(cd_nom) +")"})


    if request.user.is_authenticated:
        plantesDeJardins = p.plantedejardin_plante.all()
        jardins = set(j.jardin for j in plantesDeJardins)
        graines = p.graine_set.all()
        grainotheques = set(j.grainotheque for j in graines)
        from pygbif import occurrences
        import re
        #infos = occurrences.search(q=p.LB_NOM)
        infos = occurrences.search(scientificName=p.LB_NOM)
        infos2 = set(re.findall("(https:\/\/inaturalist-open-data\S+(?:png|jpe?g|gif))", str(infos)))
    else:
        jardins, grainotheques, infos2 = [], [], []


    return render(request, "jardins/plante.html", {"plante":p, "jardins":jardins, "grainotheques":grainotheques, "infos2":infos2})


def voir_plante_nom(request):
    cd_nom = int(request.GET["nom"])
    return redirect('jardins:voir_plante', cd_nom=cd_nom)

def voir_plante_recherche(request):
    cd_nom = int(request.GET["plante"])
    return redirect('jardins:voir_plante', cd_nom=cd_nom)


class PlanteAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Don't forget to filter out results depending on the visitor !
        if not self.request.user.is_authenticated:
            return Plante.objects.none()

        qs = Plante.objects.filter().order_by("NOM_VERN")

        if self.q:
            qs = qs.filter(Q(NOM_VERN__istartswith=self.q) | Q(NOM_VERN__icontains=self.q)| Q(LB_NOM__icontains=self.q)).order_by("NOM_VERN")

        return qs



@login_required
def ajouter_plante(request):
    form = Plante_rechercheForm(request.POST or None)
    plante = ""
    if form.is_valid():
        plante = form.save(commit=False)

    return render(request, "jardins/ajouter_plante.html", {"form":form, "plante":plante})

def chercher_plante(request):
    recherche = str(request.GET.get('id_recherche')).lower()
    plante_list = []
    if recherche:
        plante_list = Plante.objects.filter(Q(CD_SUP__lower__icontains=recherche) |
                                              Q(LB_NOM__lower__icontains=recherche) |
                                              Q(NOM_COMPLET__icontains=recherche) |
                                              Q(LB_AUTEUR__lower__icontains=recherche) |
                                              Q(NOM_VERN__lower__icontains=recherche) |
                                              Q(FR__lower__icontains=recherche)).distinct()

    return render(request, 'jardins/plante_recherche.html', {'recherche':recherche, 'plante_list':plante_list,})


def ajouterJardin_intro(request):
    if request.user.is_authenticated:
        return redirect('jardins:jardin_ajouter')
    else:
        return render(request, 'jardins/jardin_ajouterAnonyme.html', )


class AjouterJardin(CreateView):
    model = Jardin
    template_name_suffix = '_ajouter'

    def get_form(self):
        return JardinForm(**self.get_form_kwargs())

    def form_valid(self, form):
        self.object = form.save(self.request.user)
        if self.request.user.is_anonymous:
            bot = Profil.objects.get(username='bot_permacat')
            action.send(bot, verb='jardins_nouveau_jp', action_object=self.object, url=self.object.get_absolute_url(),
                     description="Un-e anonyme a ajouté le Jardin: '%s'" % self.object.titre)
        else:
            action.send(self.request.user, verb='jardins_nouveau_jp', action_object=self.object, url=self.object.get_absolute_url(),
                     description="a ajouté le Jardin: '%s'" % self.object.titre)

        return redirect("jardins:jardin_ajouterAdresse", slug=self.object.slug)

@login_required
def jardin_ajouterAdresse(request, slug):
    jardin = get_object_or_404(Jardin, slug=slug)
    form_adresse = AdresseForm4(request.POST or None)

    if form_adresse.is_valid():
        adresse = form_adresse.save()
        jardin.adresse = adresse
        jardin.save()
        return redirect(jardin)

    return render(request, 'jardins/jardin_ajouterAdresse.html', {'jardin':jardin, 'form_adresse':form_adresse })

@login_required
def jardin_ajouterSalon(request, slug):
    form = SalonJardinForm(request.POST or None)
    jardin = get_object_or_404(Jardin, slug=slug)
    if form.is_valid():
        salon = form.save(request, jardin)
        return redirect(salon)

    return render(request, 'jardins/jardin_ajouterSalon.html', {'form': form, 'jardin':jardin})

@login_required
def jardin_ajouterPlante_pk(request, jardin_pk, plante_pk):
    jardin = get_object_or_404(Jardin, pk=jardin_pk)
    plante = Plante.objects.get(pk=plante_pk)
    form = PlanteDeJardinForm(request.POST or None)
    form_infos = InfoPlanteForm(request.POST or None)
    if form.is_valid() and form_infos.is_valid():
        infos = form_infos.save()
        planteDeJardin = form.save(jardin, infos, plante)
        return redirect(jardin)

    return render(request, 'jardins/jardin_ajouterPlante_pk.html', {'jardin':jardin, 'form':form , 'form_infos':form_infos , "plante":plante})

@login_required
def ajouterPlante_monJardin(request, plante_pk):
    jardins = request.user.get_jardins

    if not 'jardin_courant_pk' in request.session:
        if len(jardins) == 0:
            return render(request, 'jardins/jardin_pasDeJardinEnregistre.html', {})
        elif len(jardins) == 1:
            request.session['jardin_courant_pk'] = jardins[0].pk
            return redirect('jardins:jardin_ajouterPlante_pk', jardin_pk=jardins[0].pk, plante_pk=plante_pk)
        else:
            form = ChoisirMonJardinForm(request, request.POST or None)

        if form.is_valid():
            request.session['jardin_courant_pk'] = form.cleaned_data['jardin'].pk
            return redirect('jardins:jardin_ajouterPlante_pk', jardin_pk=form.cleaned_data['jardin'].pk, plante_pk=plante_pk)

        return render(request, 'jardins/jardin_ChoisirMonJardin.html', {'form': form,})
    else:
        return redirect('jardins:jardin_ajouterPlante_pk', jardin_pk=request.session.get('jardin_courant_pk'), plante_pk=plante_pk)



@login_required
def voir_autreJardin(request):
    jardins = request.user.get_jardins
    if len(jardins) == 0:
        return render(request, 'jardins/jardin_pasDeJardinEnregistre.html', {})
    elif len(jardins) == 1:
        request.session['jardin_courant_pk'] = jardins[0].pk
        return redirect(jardins[0])
    else:
        form = ChoisirMonJardinForm(request, request.POST or None)

    if form.is_valid():
        request.session['jardin_courant_pk'] = form.cleaned_data['jardin'].pk
        return redirect(form.cleaned_data['jardin'])

    return render(request, 'jardins/jardin_ChoisirMonJardin.html', {'form': form,})


@login_required
def voir_monJardin(request):
    jardins = request.user.get_jardins
    if not 'jardin_courant_pk' in request.session:
        if len(jardins) == 0:
            return render(request, 'jardins/jardin_pasDeJardinEnregistre.html', {})
        elif len(jardins) == 1:
            request.session['jardin_courant_pk'] = jardins[0].pk
            return redirect(jardins[0])
        else:
            form = ChoisirMonJardinForm(request, request.POST or None)

        if form.is_valid():
            request.session['jardin_courant_pk'] = form.cleaned_data['jardin'].pk
            return redirect(form.cleaned_data['jardin'])

        return render(request, 'jardins/jardin_ChoisirMonJardin.html', {'form': form,})
    else:
        return redirect(Jardin.objects.get(pk=request.session.get('jardin_courant_pk')))



@login_required
def graino_ajouterGraine_pk(request, graino_pk, plante_pk):
    graino = get_object_or_404(Grainotheque, pk=graino_pk)
    plante = Plante.objects.get(pk=plante_pk)
    form = GraineForm(request.POST or None)
    form_infos = InfoGraineForm(request.POST or None)
    if form.is_valid() and form_infos.is_valid():
        infos = form_infos.save()
        graine = form.save(graino, infos, plante)
        return redirect(graino)

    return render(request, 'jardins/grainotheque_ajouterGraine_pk.html', {'graino':graino, 'form':form , 'form_infos':form_infos, "plante":plante})



@login_required
def ajouterPlante_maGrainotheque(request, plante_pk):
    graino = request.user.get_grainotheques
    if len(graino) == 0:
        return render(request, 'jardins/jardin_pasDeGrainothequeEnregistre.html', {})
    elif len(graino) == 1:
        return redirect('jardins:graino_ajouterGraine_pk', graino_pk=graino[0].pk, plante_pk=plante_pk)
    else:
        form = ChoisirMaGrainothequeForm(request, request.POST or None)

    if form.is_valid():
        return redirect('jardins:graino_ajouterGraine_pk',graino_pk=form.cleaned_data['grainotheque'].pk, plante_pk=plante_pk)

    return render(request, 'jardins/grainotheque_choisirMaGrainotheque.html', {'form': form,})

@login_required
def voir_maGrainotheque(request):
    graino = request.user.get_grainotheques
    if len(graino) == 0:
        return render(request, 'jardins/jardin_pasDegrainothequeEnregistre.html', {})
    elif len(graino) == 1:
        return redirect(graino[0])
    else:
        form = ChoisirMaGrainothequeForm(request, request.POST or None)

    if form.is_valid():
        return redirect(form.cleaned_data['grainotheque'])

    return render(request, 'jardins/grainotheque_choisirMaGrainotheque.html', {'form': form,})


@login_required
def jardin_modifierAdresse(request, slug):
    jardin = get_object_or_404(Jardin, slug=slug)
    form_adresse = AdresseForm4(request.POST or None, instance=jardin.adresse)

    if form_adresse.is_valid():
        adresse = form_adresse.save()
        jardin.adresse = adresse
        jardin.save()
        return redirect(jardin)

    return render(request, 'jardins/jardin_modifierAdresse.html', {'adresse':jardin.adresse, 'form_adresse':form_adresse })

def carte_jardins(request):
    jardins = Jardin.objects.all().order_by("titre")
    nbProf = len(jardins)

    if not request.user.is_authenticated:
        jardins = jardins.filter(visibilite_annuaire='0')
    else:
        jardins = jardins.filter(Q(visibilite_annuaire='0') | Q(visibilite_annuaire='1') )

    if "lettre" in request.GET:
        jardins = jardins.filter(titre__istartswith=request.GET["lettre"])

    jardins_filtres = JardinCarteFilter(request.GET, queryset=jardins)


    graino = Grainotheque.objects.all().order_by("titre")
    nbProf = len(graino)

    if not request.user.is_authenticated:
        graino = graino.filter(visibilite_annuaire='0')
    else:
        graino = graino.filter(Q(visibilite_annuaire='0') | Q(visibilite_annuaire='1') )

    if "lettre" in request.GET:
        graino = graino.filter(titre__istartswith=request.GET["lettre"])

    graino_filtres = GrainoCarteFilter(request.GET, queryset=graino)

    titre = "Carte des jardins et des grainothèques Catalanes"

    if request.user.is_authenticated:
        mesJardins = Jardin.objects.filter(auteur=request.user)
        mesGraino = Grainotheque.objects.filter(auteur=request.user)
    else:
        mesJardins, mesGraino = [], []
    return render(request, 'jardins/carte_jardins.html', {'jardins_filtres':jardins_filtres, 'graino_filtres':graino_filtres, 'titre': titre, 'mesJardins':mesJardins, 'mesGraino':mesGraino} )

def carte_graino(request):
    graino = Grainotheque.objects.all().order_by("titre")
    nbProf = len(graino)

    if not request.user.is_authenticated:
        graino = graino.filter(visibilite_annuaire='0')
    else:
        graino = graino.filter(Q(visibilite_annuaire='0') | Q(visibilite_annuaire='1') )

    if "lettre" in request.GET:
        graino = graino.filter(titre__istartswith=request.GET["lettre"])

    graino_filtres = GrainoCarteFilter(request.GET, queryset=graino)
    #graino_filtres = graino
    titre = "Carte des grainothèques "

    return render(request, 'jardins/carte_graino.html', {'filter':graino_filtres, 'titre': titre, })


class JardinDetailView(DetailView):
    model = Jardin

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context["user_inscrit"] = InscriptionJardin.objects.filter(user=self.request.user, jardin=self.object).exists()
        context["adresse_visible"] = self.object.visibilite_annuaire == '0' or (self.object.visibilite_annuaire == '1' and self.request.user.is_authenticated)
        context["salons"] = Salon.objects.filter(jardin=self.object)
        context["grainotheques"] = Grainotheque.objects.filter(jardin=self.object)
        context["plantes"] = PlanteDeJardin.objects.filter(jardin=self.object).order_by("plante__LB_NOM")
        return context

class AjouterGrainotheque(CreateView):
    model = Grainotheque
    template_name_suffix = '_ajouter'

    def get_form(self):
        return GrainothequeForm(current_user=self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        self.object = form.save(self.request.user)
        action.send(self.request.user, verb='jardins_nouvelleGrainotheque_jp', action_object=self.object, url=self.object.get_absolute_url(),
                     description="a ajouté la Grainothèque: '%s'" % self.object.titre)
        if self.object.jardin:
            adresse = self.object.jardin.adresse
            adresse.pk = None
            adresse.save()
            self.object.adresse = adresse
            self.object.save()
        else:
            return redirect("jardins:grainotheque_ajouterAdresse", slug=self.object.slug)
        return HttpResponseRedirect(self.get_success_url())


@login_required
def grainotheque_ajouterAdresse(request, slug):
    grainotheque = get_object_or_404(Grainotheque, slug=slug)
    form_adresse = AdresseForm4(request.POST or None)

    if form_adresse.is_valid():
        adresse = form_adresse.save()
        grainotheque.adresse = adresse
        grainotheque.save()
        return redirect(grainotheque)

    return render(request, 'jardins/grainotheque_ajouterAdresse.html', {'grainotheque':grainotheque, 'form_adresse':form_adresse })


@login_required
def grainotheque_modifierAdresse(request, slug):
    grainotheque = get_object_or_404(Grainotheque, slug=slug)
    form_adresse = AdresseForm4(request.POST or None, instance=grainotheque.adresse)

    if form_adresse.is_valid():
        adresse = form_adresse.save()
        grainotheque.adresse = adresse
        grainotheque.save()
        return redirect(grainotheque)

    return render(request, 'jardins/grainotheque_modifierAdresse.html', {'adresse':grainotheque.adresse, 'form_adresse':form_adresse })

@login_required
def grainotheque_supprimerGraines(request, slug):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    grainotheque = get_object_or_404(Grainotheque, slug=slug)

    for g in Graine.objects.filter(grainotheque=grainotheque):
       g.delete()

    return redirect("jardins:grainotheque_lire", slug=slug)

class GrainothequeDetailView(DetailView):
    model = Grainotheque

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["graines"] = Graine.objects.filter(grainotheque=self.object).order_by("nom")
        context["adresse_visible"] = self.object.visibilite_annuaire == '0' or (self.object.visibilite_annuaire == '1' and self.request.user.is_authenticated)
        return context

class ModifierInfoGraine(UpdateView):
    model = InfoGraine
    form_class = InfoGraineForm
    template_name_suffix = '_modifier'

class ModifierJardin(UpdateView):
    model = Jardin
    template_name_suffix = '_modifier'

    def get_form(self):
        return JardinChangeForm(current_user=self.request.user, **self.get_form_kwargs())

class SupprimerJardin(DeleteView):
    model = Jardin
    template_name_suffix = '_supprimer'

    def get_success_url(self):
        return reverse('jardins:carte_jardins')


@login_required
def jardin_ajouterPlante(request, slug):
    jardin = get_object_or_404(Jardin, slug=slug)
    form = PlanteDeJardinForm(request.POST or None)
    form_infos = InfoPlanteForm(request.POST or None)
    plant_form = Plante_rechercheForm(None)
    if form.is_valid() and form_infos.is_valid():
          #  return redirect("jardins:voir_plante", cd_nom=str(self.qs[0].CD_NOM))
        infos = form_infos.save()
        plante = Plante.objects.get(CD_NOM=int(request.POST["plante"]))
        planteDeJardin = form.save(jardin, infos, plante)
        return redirect(jardin)

    return render(request, 'jardins/jardin_ajouterPlante.html', {'jardin':jardin, 'form':form , 'plant_form':plant_form , 'form_infos':form_infos })


@login_required
def jardin_modifierPlante(request, slug_jardin, pk):
    plante = PlanteDeJardin.objects.get(pk=pk)
    jardin = get_object_or_404(Jardin, slug=slug_jardin)
    form_infos = InfoPlanteForm(request.POST or None, instance=plante.infos)
    if form_infos.is_valid():
        infos = form_infos.save()
        return redirect(jardin)

    return render(request, 'jardins/jardin_modifierPlante.html', {'jardin':jardin, 'plante':plante, 'form_infos':form_infos })


@login_required
def jardin_supprimerPlante(request, slug_jardin, pk):
    PlanteDeJardin.objects.get(jardin__slug=slug_jardin, pk=pk).delete()
    return redirect("jardins:jardin_lire", slug=slug_jardin)



class PlanteDJDeleteView(DeleteView):
    model = PlanteDeJardin
    template_name_suffix = '_supprimer'

    def get_object(self):
        self.jardin = Jardin.objects.get(slug=self.kwargs['slug_jardin'])
        ad = PlanteDeJardin.objects.get(pk=self.kwargs['pk'], jardin=self.jardin)
        return ad

    def get_success_url(self):
        return self.jardin.get_absolute_url()


@login_required
def jardin_supprimerPlantes(request, slug_jardin):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    jardin = get_object_or_404(Jardin, slug=slug_jardin)

    for g in PlanteDeJardin.objects.filter(jardin=jardin):
       g.delete()

    return redirect("jardins:jardin_lire", slug=slug_jardin)

class ModifierInfoPlante(UpdateView):
    model = InfoPlante
    form_class = InfoPlanteForm
    template_name_suffix = '_modifier'

class ModifierGrainotheque(UpdateView):
    model = Grainotheque
    form_class = GrainothequeChangeForm
    template_name_suffix = '_modifier'

    def get_form(self):
        return GrainothequeChangeForm(current_user=self.request.user, **self.get_form_kwargs())

class SupprimerGrainotheque(DeleteView):
    model = Grainotheque
    template_name_suffix = '_supprimer'

    def get_success_url(self):
        return reverse('jardins:carte_graino')

@login_required
def graino_ajouterGraine(request, slug):
    graino = get_object_or_404(Grainotheque, slug=slug)
    form = GraineForm(request.POST or None)
    form_infos = InfoGraineForm(request.POST or None)
    plant_form = Plante_rechercheForm(None)
    if form.is_valid() and form_infos.is_valid():
          #  return redirect("jardins:voir_plante", cd_nom=str(self.qs[0].CD_NOM))
        infos = form_infos.save()
        plante = Plante.objects.get(CD_NOM=int(request.POST["plante"]))
        graine = form.save(graino, infos, plante)
        return redirect(graino)

    return render(request, 'jardins/grainotheque_ajouterGraine.html', {'graino':graino, 'form':form , 'plant_form':plant_form , 'form_infos':form_infos })


@login_required
def graino_modifierGraine(request, slug_graino, pk):
    graine = Graine.objects.get(pk=pk)
    graino = get_object_or_404(Grainotheque, slug=slug_graino)
    form = GraineForm(request.POST or None, instance=graine)
    form_infos = InfoGraineForm(request.POST or None, instance=graine.infos)
    if form.is_valid() and form_infos.is_valid():
        infos = form_infos.save()
        graine = form.save(graino, infos, graine.plante)
        return redirect(graino)

    return render(request, 'jardins/grainotheque_modifierGraine.html', {'graino':graino, 'graine':graine, 'form':form , 'form_infos':form_infos })

@login_required
def inscriptionJardin(request, slug):
    jardin = get_object_or_404(Jardin, slug=slug)
    if not InscriptionJardin.objects.filter(user=request.user, jardin=jardin):
        inscript = InscriptionJardin(user=request.user, jardin=jardin)
        inscript.save()
        action.send(request.user, verb='jardins_inscription_jp', action_object=jardin, url=jardin.get_absolute_url(),
                     description="s'est inscrit.e au jardin: '%s'" % jardin.titre)

    return redirect(jardin.get_absolute_url())

@login_required
def annulerInscription(request, slug):
    jardin = get_object_or_404(Jardin, slug=slug)
    inscript = InscriptionJardin.objects.filter(user=request.user, jardin=jardin)
    inscript.delete()
    action.send(request.user, verb='jardins_desinscription_jp', action_object=jardin, url=jardin.get_absolute_url(),
                 description="s'est désinscrit du jardin: '%s'" % jardin.titre)
    return redirect(jardin.get_absolute_url())

@login_required
def contacterInscritsJardin(request, slug):

    jardin = get_object_or_404(Jardin, slug=slug)
    inscrits = [x.user.email for x in InscriptionJardin.objects.filter(jardin=jardin)]
    form = ContactParticipantsForm(request.POST or None, )
    try:
        referent = Profil.objects.get(username=jardin.referent)
        inscrits.append(referent.email)
    except:
        pass
    if form.is_valid():
        sujet = "[Jardins] Au sujet dU Jardin '" + jardin.titre + "' "
        message_html = str(request.user.username) + " (" + str(
            request.user.email) + ") a écrit le message suivant aux participants : \n"
        message_html += form.cleaned_data['msg']
        message_html += "\n (ne pas répondre à ce message)"
        messagetxt = BeautifulSoup(message_html).get_text()
        send_mass_html_mail([(sujet, messagetxt, message_html, SERVER_EMAIL, inscrits)], fail_silently=False)

    return render(request, 'jardins/jardin_contacterParticipants.html',
                  {'jardin': jardin, 'form': form, 'inscrits': inscrits})


@login_required
def carte_jardiniers(request):
    asso = Asso.objects.get(slug="jp")
    profils_total = asso.getProfils()
    nbProf = len(profils_total)
    profils = asso.getProfils_Annuaire()
    if "lettre" in request.GET:
        profils = profils.filter(username__istartswith=request.GET["lettre"])
    profils_filtres = ProfilCarteFilter(request.GET, queryset=profils)
    #profils_filtres = profils
    titre = "Carte des Jardinier-es"

    return render(request, 'jardins/carte_cooperateurs.html', {'filter':profils_filtres, 'titre': titre, "asso":asso} )
