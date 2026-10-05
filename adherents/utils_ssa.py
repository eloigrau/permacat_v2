from django.contrib.auth.decorators import login_required

from .models import Contact, ProjetPhoning
from bourseLibre.models import Asso, Adresse
from bourseLibre.utils import testIsMembreAsso, testIsMembreAsso_bool, TestMembreAssoMixin, TestBureauAssoMixin, UserPassesTestMixin

from django.shortcuts import render
import csv
from django import forms
try:
    import pandas as pd
except:
    pass
import io

class csvFile_form(forms.Form):
    fichier_csv_clients = forms.FileField(label="Selectionner CSV Orga", required=True, )
    fichier_csv_produits = forms.FileField(label="Selectionner CSV Produits", required=False, )

@login_required
def lire_csv_clients(request, csv_reader):
    if not request.user.is_superuser:
        return "Déso, Vous n'etes pas autorisé a utiliser cette fonctionnalité"
    asso = Asso.objects.get(slug=request.session["asso_slug"])
    projet_courant = ProjetPhoning.objects.get(pk=request.session['projet_courant_pk'] )
    msg = ""
    for i, line in enumerate(csv_reader):
        # if i == 0:
        #    continue
        try:
            cles = line.keys()
            if "Nom" in line and line["Nom"] and Contact.objects.filter(asso=asso,
                    nom=line["Nom"]):
                msg += "<p> DEJA  " + str(line) + "#" + line["Nom"] + "#</p>"
                continue

            if ("rue" in line and line["rue"]) or ("code_postal" in line and line["code_postal"]) or ("Commune" in line and line["Commune"]) or ("Téléphone" in line and line["Téléphone"]):
                adres, created = Adresse.objects.get_or_create(rue=line["rue"] if 'rue' in cles else "",
                                                               code_postal=line["code_postal"] if 'code_postal' in cles else "",
                                                               commune=line["Commune"] if 'Commune' in cles else "",
                                                               telephone=line["Téléphone"] if 'telephone' in cles else "")
                adres.save()
            else:
                adres, created = Adresse.objects.get_or_create(rue="adresse inconnue")

            listeColComm = ["commentaire", "Fonction"]

            commentaire = "; ".join([ line[x] if x in cles else "" for x in listeColComm])
            contact, created = Contact.objects.get_or_create(
                nom=line["nom"] if 'nom' in cles else "",
                prenom=line["prenom"] if 'prenom' in cles else "",
                adresse=adres,
                email=line["email"] if 'email' in cles else "",
                commentaire=commentaire,
                referent=line["RÉFÉRENT.ES"] if 'RÉFÉRENT.ES' in cles else "",
                nom_structure=line["DÉNOMINATIONSTRUCTURE"] if 'DÉNOMINATIONSTRUCTURE' in cles else "",
                type_structure="Organisations alimentaires",
                projet=projet_courant,
            )
            if created:
                msg += "<p> ajoute " + str(line) + " / " + str(contact) + "</p>"
            else:
                msg += "<p>  deja present " + str(line) + " / " + str(contact) + "</p>"

        except Exception as e:
            msg += "<p>Erreur " + str(e) + " > " + str(i) + " " + str(line)
    return msg


@login_required
def import_csv(request):
    def lire_clients(request, fichier_csv_clients):
        with io.TextIOWrapper(fichier_csv_clients, encoding="utf-8") as data:
            csv_reader = csv.DictReader(data, delimiter=',')
            if not "Nom" in csv_reader.fieldnames and not "Mail" in csv_reader.fieldnames:
                m = "Erreur : Le fichier '" + str(fichier_csv_clients) + "'" +" n'a pas de colonne 'Nom' ni 'Mail' (sans espace)"
                return render(request, '', {"liste_tel": str(csv_reader.fieldnames), "message": m})
            m = str(csv_reader.fieldnames)
            m += lire_csv_clients(request, csv_reader)

        m += "Fichier client lu\n"
        return m

    if not request.user.is_superuser:
        return "Déso, Vous n'etes pas autorisé a utiliser cette fonctionnalité"

    testIsMembreAsso(request, request.session["asso_slug"])
    if request.POST:
        form = csvFile_form(request.POST, request.FILES)
        if form.is_valid():
            m = ""
            fichier_csv_clients = form.cleaned_data['fichier_csv_clients']
            m += lire_clients(request, fichier_csv_clients)

            return render(request, 'compta/admin_utils.html', {"message": m, "title": "Resultat imports factures"})
    else:
        form = csvFile_form()

    return render(request, 'compta/admin_utils.html', {"form": form, "title": "Lancer imports factures"})
