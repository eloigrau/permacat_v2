from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

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
    type_fic = forms.ChoiceField(label="Production",
                                       help_text="Selectionner la production correspondant à votre code APE dans la liste",
                                      choices=(('1', "Orgas"), ("2","Autre")))
    #fichier_csv_produits = forms.FileField(label="Selectionner CSV Produits", required=False, )

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
            if "Nom" in line and line["Nom"] and Contact.objects.filter(projet__asso=asso,
                    nom=line["Nom"]):
                msg += "<p> DEJA  " + str(line) + "#" + line["Nom"] + "#</p>"
                continue

            if ("rue" in line and line["rue"]) or ("CP" in line and line["CP"]) or ("Commune" in line and line["Commune"]) or ("Téléphone" in line and line["Téléphone"]):
                adres, created = Adresse.objects.get_or_create(rue=line["rue"] if 'rue' in cles else "",
                                                               code_postal=line["CP"] if 'CP' in cles else "",
                                                               commune=line["Commune"] if 'Commune' in cles else "",
                                                               telephone=line["Téléphone"] if 'Téléphone' in cles else "")
                adres.save()
            else:
                adres, created = Adresse.objects.get_or_create(rue="adresse inconnue")

            listeColComm = ["COMMENTAIRES", "Fonction"]

            commentaire = "; ".join([ line[x] if x in cles else "" for x in listeColComm])
            contact, created = Contact.objects.get_or_create(
                nom=line["Nom"] if 'Nom' in cles else "",
                prenom=line["Prénom"] if 'Prénom' in cles else "",
                adresse=adres,
                email=line["Mail"] if 'Mail' in cles else "",
                commentaire=commentaire,
                referent=line["RÉFÉRENT.ES"] if 'RÉFÉRENT.ES' in cles else "",
                nom_structure=line["DENOMINATIONSTRUCTURE"] if 'DENOMINATIONSTRUCTURE' in cles else "",
                type_structure=line["TYPEDORGANISATION"] if 'TYPEDORGANISATION' in cles else "",
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
def lire_csv_clients2(request, csv_reader):
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
            if "Nom" in line and line["Nom"] and Contact.objects.filter(projet=projet_courant,
                    nom=line["Nom"]):
                msg += "<p> DEJA  " + str(line) + "#" + line["Nom"] + "#</p>"
                continue

            if ("rue" in line and line["rue"]) or ("CP" in line and line["CP"]) or ("Commune" in line and line["Commune"]) or ("Téléphone" in line and line["Téléphone"]):
                adres, created = Adresse.objects.get_or_create(rue=line["rue"] if 'rue' in cles else "",
                                                               code_postal=line["CP"] if 'CP' in cles else "",
                                                               commune=line["Commune"] if 'Commune' in cles else "",
                                                               telephone=line["Téléphone"] if 'Téléphone' in cles else "")
                adres.save()
            else:
                adres, created = Adresse.objects.get_or_create(rue="adresse inconnue")

            listeColComm = ["COMMENTAIRES", "COMMENTAIRES2"]

            commentaire = "; ".join([ line[x] if x in cles else "" for x in listeColComm])
            contact, created = Contact.objects.get_or_create(
                nom=line["Nom"] if 'Nom' in cles else "",
                prenom=line["Prénom"] if 'Prénom' in cles else "",
                adresse=adres,
                email=line["Mail"] if 'Mail' in cles else "",
                commentaire=commentaire,
                referent=line["RÉFÉRENT.ES"] if 'RÉFÉRENT.ES' in cles else "",
                nom_structure=line["DENOMINATIONSTRUCTURE"] if 'DENOMINATIONSTRUCTURE' in cles else "",
                type_structure=line["TYPEDORGANISATION"] if 'TYPEDORGANISATION' in cles else "",
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
def import_csv_orga_ssa(request, asso_slug):
    def lire_clients(request, fichier_csv_clients, type=1):
        with io.TextIOWrapper(fichier_csv_clients, encoding="utf-8") as data:
            csv_reader = csv.DictReader(data, delimiter=',')
            if not "Nom" in csv_reader.fieldnames and not "Mail" in csv_reader.fieldnames:
                m = "Erreur : Le fichier '" + str(fichier_csv_clients) + "'" +" n'a pas de colonne 'Nom' ni 'Mail' (sans espace)"
                return render(request, '', {"liste_tel": str(csv_reader.fieldnames), "message": m})
            m = str(csv_reader.fieldnames)
            if type == "1":
                m += lire_csv_clients(request, csv_reader)
            elif type == "2":
                m += lire_csv_clients2(request, csv_reader)
            else:
                m += "Type de fichier non reconnu"

        m += "Fichier client lu\n"
        return m

    if not request.user.is_superuser:
        return "Déso, Vous n'etes pas autorisé a utiliser cette fonctionnalité"

    testIsMembreAsso(request, request.session["asso_slug"])
    request.session["asso_slug"] = asso_slug

    if not request.session["asso_slug"] == "ssa":
        return HttpResponseForbidden("l'asso doit etre SSA pas une autre !")

    if request.POST:
        form = csvFile_form(request.POST, request.FILES)
        if form.is_valid():
            m = ""
            fichier_csv_clients = form.cleaned_data['fichier_csv_clients']
            m += lire_clients(request, fichier_csv_clients, form.cleaned_data['type_fic'])

            return render(request, 'adherents/contact_outils_accueil.html', {"message": m, "title": "Resultat imports factures"})
    else:
        form = csvFile_form()

    return render(request, 'adherents/admin_utils.html', {"form": form, "title": "Lancer imports factures"})


import requests


def get_code_postal(nom_commune: str):
    url = "https://api-adresse.data.gouv.fr/search/"
    params = {
        "q": nom_commune,
        "type": "municipality",
        "limit": 1
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        features = data.get("features", [])
        if features:
            return features[0]["properties"]["postcode"]
    return None

@login_required
def nettoyer_SSA(request, asso_slug):
    if not request.user.is_superuser:
        return "Déso, Vous n'etes pas autorisé a utiliser cette fonctionnalité"

    testIsMembreAsso(request, "ssa")
    m = ""
    for contact in Contact.objects.filter(projet__asso__slug="ssa"):
        if contact.adresse:
            if contact.adresse.commune:
                try:
                    code_postal = get_code_postal(contact.adresse.commune)
                    if code_postal:
                        contact.adresse.code_postal = code_postal
                        contact.adresse.save()
                    m += "<p>Adresse corrigee " + str(contact.adresse)+" " + str(contact.adresse.code_postal)+"</p>"
                except Exception as e:
                    m += "ErreurGet CP " + str(e) +" ; " + str(contact.adresse.commune) + " " + str(contact.id)

            if contact.commentaire == " ; ":
                contact.commentaire = ""
                contact.save()
                m += "<p>commentaire corrige " + str(contact)+"</p>"

    return render(request, 'adherents/contact_outils_accueil.html', {"message": m, "title": "Resultat nettoyage SSA"})
