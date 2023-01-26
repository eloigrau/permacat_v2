from django.shortcuts import render, redirect
from django.views.generic import ListView, UpdateView, DeleteView
from .models import Plante, DBStatut_inpn, DBRang_inpn, DBHabitat_inpn, DBVern_inpn, DB_importeur
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, HttpResponseRedirect
import csv
from django.db.models import Q
from bourseLibre.settings import PROJECT_ROOT, os, LOCALL

@login_required
def accueil(request):
    return render(request, "jardins/accueil.html", {'msg':"Tout est pret"})


def get_dossier_db(nomfichier):
    if LOCALL:
        return "/home/tchenrezi/Téléchargements/TAXREF_v16_2022/" + nomfichier

    return os.path.abspath(os.path.join(PROJECT_ROOT, "../../../", nomfichier))

@login_required
def import_db_inpn_0(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    msg =" impor plantes "
    filename = get_dossier_db("TAXREFv16.txt")
    if 'reset' in request.GET:
        Plante.objects.all().delete()
    if 'j_max' in request.GET:
        j_max= int(request.GET["j_max"])
    else:
        j_max= 800000
    if 'j_min' in request.GET:
        j_min= int(request.GET["j_min"])
    else:
        j_min= 0
    j = 0
    k = 0
    dbg, created = DB_importeur.objects.get_or_create(nom='db_taxref')
    dbg.lg_debut = dbg.lg_fin
    msg +=" j_min" + str(j_min) + " jmax" + str(j_max)
    try:
        with open(filename, 'r') as data:
            for i, line in enumerate(csv.DictReader(data, delimiter="\t")):
                if i > j_max:
                    break
                if i < j_min:
                    continue
                if line["REGNE"] and line["NOM_VERN"] and (line["REGNE"] == "Plantae"):
                    if Plante.objects.filter(CD_NOM=line["CD_NOM"]).exists():
                        continue

                    if Plante.objects.filter(LB_NOM=line["LB_NOM"]).exists():
                        p = Plante.objects.get(LB_NOM=line["LB_NOM"])
                        if not p.infos_supp:
                            p.infos_supp = line["URL"] + "; "
                        elif line["CD_NOM"] not in p.infos_supp:
                            p.infos_supp = p.infos_supp + line["URL"] + "; "
                        p.save()
                    elif Plante.objects.filter(NOM_VERN=line["NOM_VERN"]).exists() :
                        p = Plante.objects.get(NOM_VERN=line["NOM_VERN"])
                        if not p.infos_supp:
                            p.infos_supp = line["URL"] + "; "
                        elif line["CD_NOM"] not in p.infos_supp:
                            p.infos_supp = p.infos_supp + line["URL"] + "; "
                        p.save()
                    else:
                        try:
                            if not line["CD_SUP"]:
                                line["CD_SUP"] = 0
                            Plante(**line).save()
                            j += 1
                        except Exception as e:
                            msg += "<p> erreur " + str(line) + str(e) + "</p>"

    except Exception as e:
        msg += "<p> ERR " + str(line) + str(e) + "</p>"
    msg += "<p>j total" + str(j) + "</p>"
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

        if "recherche" in self.request.GET:
            context['recherche'] = self.request.GET["recherche"]
        else:
            context['recherche'] = "Trouver une plante..."
        if 'categorie' in self.request.GET:
            context['typeFiltre'] = "categorie"
           # context['categorie_courante'] = [x[1] for x in Choix.type_atelier if x[0] == self.request.GET['categorie']][0]
        if 'ordreTri' in self.request.GET:
            context['typeFiltre'] = "ordreTri"

        return context


@login_required
def voir_plante(request, cd_nom):
    p = get_object_or_404(Plante, CD_NOM=int(cd_nom))
    return render(request, "jardins/plante.html", {"plante":p})


@login_required
def voir_plante_nom(request):
    cd_nom = int(request.GET["nom"])
    try:
        p = Plante.objects.get(CD_NOM=int(cd_nom))
    except:
        return render(request, "jardins/plante.html", {"msg":"plante introuvable"})

    return render(request, "jardins/plante.html", {"plante":p})
