from django.shortcuts import render, redirect
from django.views.generic import ListView, UpdateView, DeleteView
from .models import Plante, DBStatut_inpn, DBRang_inpn, DBHabitat_inpn, DBVern_inpn
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, HttpResponseRedirect
import csv
from django.db.models import Q
from bourseLibre.settings import PROJECT_ROOT, os

@login_required
def accueil(request):
    return render(request, "jardins/accueil.html", {'msg':"Tout est pret"})


def get_dossier_db(nomfichier):
    return os.path.abspath(os.path.join(PROJECT_ROOT, "../../../", nomfichier))

@login_required
def import_db_inpn_0(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    try:
        filename = get_dossier_db("TAXREFv16.txt")
        if 'reset' in request.GET:
            Plante.objects.all().delete()
        if 'nb_plantes' in request.GET:
            j_max= int(request.GET["nb_plantes"])
        else:
            j_max= 800000
        j = 0
        msg=" impor plantes jmax" + str(j_max)
        with open(filename, 'r') as data:
            for i, line in enumerate(csv.DictReader(data, delimiter="\t")):
                if j > j_max:
                    break
                if line["REGNE"] and line["NOM_VERN"] and (line["REGNE"] == "Plantae"):
                    if Plante.objects.filter(CD_NOM=line["CD_NOM"]).exists():
                        pass

                    if Plante.objects.filter(LB_NOM=line["LB_NOM"]).exists():
                        p = Plante.objects.get(LB_NOM=line["LB_NOM"])
                        if line["CD_NOM"] not in p.infos_supp:
                            p.infos_supp = p.infos_supp + str(line["CD_NOM"]) + "; "
                            p.save()
                    elif Plante.objects.filter(NOM_VERN=line["NOM_VERN"]).exists() :
                        p = Plante.objects.get(NOM_VERN=line["NOM_VERN"])
                        if line["CD_NOM"] not in p.infos_supp:
                            p.infos_supp = p.infos_supp + str(line["CD_NOM"]) + "; "
                            p.save()
                    else:
                        try:
                            Plante(**line).save()
                            j = j+1
                        except:
                            msg += "<p>" + str(line) + "</p>"
    except Exception as e:
            msg += "<p>" + str(e) + "</p>"

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
            self.qs = Plante.objects.filter(Q(NOM_VERN__icontains=params['recherche']) | Q(NOM_COMPLET__icontains=params['recherche'])| Q(LB_NOM__icontains=params['recherche']))

            if 'lettre' in params:
                self.qs = self.qs.filter(NOM_VERN__istartswith=params['lettre'])
        elif 'lettre' in params:
            self.qs = Plante.objects.filter(NOM_VERN__istartswith=params['lettre'])

        if "categorie" in params:
            self.qs = self.qs.filter(categorie=params['categorie'])

        if "ordreTri" in params:
            self.qs = self.qs.order_by(params['ordreTri'])
        else:
            self.qs = self.qs.order_by('-start_time', 'categorie', '-date_dernierMessage', )

        if self.qs.count() == 1:
            return redirect("jardins:voir_plante", kwargs={"cd_nom":str(self.qs[0].CD_NOM)})

        return self.qs.order_by("NOM_VERN")

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
