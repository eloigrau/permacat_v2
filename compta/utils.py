from .models import BudgetCercle, BudgetProjet, Transaction
from .forms import TransactionForm, BudgetProjetForm, TransationChangeForm, ClientForm, AssoInfoForm, ProductForm
from django.contrib.auth.decorators import login_required
from blog.models import Projet

from .models import Client, Product, AssoInfo
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from bourseLibre.utils import testIsMembreAsso, testIsMembreAsso_bool, TestMembreAssoMixin, TestBureauAssoMixin, UserPassesTestMixin
from .models import RecuFiscal
from bourseLibre.models import Asso
import math

from .forms import FactureForm, FactureItemFormSet, FactureStatutForm
from django.shortcuts import get_object_or_404, redirect, render
from .models import Facture, DocumentStatus, DocumentType, FactureItem
import csv
from django import forms
import pandas as pd
import datetime
from bourseLibre.settings import LOCALL

class csvFile_form(forms.Form):
    fichier_csv_clients = forms.FileField(label="Selectionner CSV Clients", required=True, )
    fichier_csv_produits = forms.FileField(label="Selectionner CSV Produits", required=False, )
    fichier_csv_factures = forms.FileField(label="Selectionner CSV Factures)", required=False, )

@login_required
def lire_csv_clients(request, csv_reader):
    asso = Asso.objects.get(slug=request.session["asso_slug"])
    msg = ""
    for i, line in enumerate(csv_reader):
        # if i == 0:
        #    continue
        try:
            cles = line.keys()
            if "code" in line and line["code"] and Client.objects.filter(
                    code_client__iexact=line["code"]):
                msg += "<p> DEJACLI  " + str(line) + "#" + line["code"] + "#</p>"
                continue

            contact = Client(
                name=line["nom"] if 'nom' in cles else "",
                code_client=line["code"] if 'code' in cles else "",
                address=line["ad1"]+" "+line["ad2"]+" "+line["ad3"],
                email=line["email"] if 'email' in cles else "",
                telephone=line["telephone"] if 'telephone' in cles else "",
                infos=line["remarque1"] if 'remarque1' in cles else "",
                asso=asso
            )
            contact.save(asso)
            msg += "<p> Client_ajoute  " + str(line) + " / " + str(contact) + "</p>"

        except Exception as e:
            msg += "<p>Erreur " + str(e) + " > " + str(i) + " " + str(line)
    return msg

@login_required
def lire_csv_produits(request, csv_reader):
    asso = Asso.objects.get(slug=request.session["asso_slug"])
    msg = ""
    for i, line in enumerate(csv_reader):
        # if i == 0:
        #    continue
        try:
            cles = line.keys()
            if "code" in line and line["code"] and Product.objects.filter(
                    code_product__iexact=line["code"]):
                msg += "<p> DEJA  " + str(line) + "#" + line["code"] + "#</p>"
                continue

            try:
                tarif = float(str(line["tarif"]).replace(",",".")) if 'tarif' in cles and line["tarif"] else 0.
            except:
                tarif = float(0.0)

            obj = Product(
                name=line["nom"] if 'nom' in cles else "",
                code_product=line["code"] if 'code' in cles else "",
                description=line["a"]+" "+line["b"],
                unit_price=tarif,
                asso=asso
            )
            obj.save(asso)
            msg += "<p> ajoute  " + str(line) + " / " + str(obj) + "</p>"

        except Exception as e:
            msg += "<p>Erreur " + str(e) + " > " + str(i) + " " + str(line)
    return msg


@login_required
def lire_csv_factures(request, filename):
    asso = Asso.objects.get(slug=request.session["asso_slug"])
    asso_info = AssoInfo.objects.get(asso=asso, is_default=True)
    msg = ""

    #with pd.read_csv(filename) as df:
    df = pd.read_csv(filename, )
    for column in df:
        d = df[column]
        #msg += "<p> debut " + "#" + d[0] + "#</p>"

        try:
            client = Client.objects.get(code_client=d[0])

            date_echeance = datetime.datetime(year=int("20"+d[3].split("/")[2]),
                                                  month=int(d[3].split("/")[1]),
                                                  day=int(d[3].split("/")[0])
                                              )
        except Exception as e:
            msg += "<p> +erreur  " + str(e) + " > " + str(d[3])+" " + str(d[0])+"</p>"
            continue

        if Facture.objects.filter(number__iexact=column):
            msg += "<p> DEJAFact" + "#" + str(column) + "#</p>"
            continue

        facture, created = Facture.objects.get_or_create(
            number=column,
            client=client,
            date_echeance=date_echeance,
            asso_info=asso_info,
            asso=asso,
            status=DocumentStatus.PAID,
            is_archived=True,
        )

        if created:
            msg += "<p> +fact  " + str(facture)+" </p>"
        else:
            msg += "<p>  facture deja present " + str(facture) + "</p>"

        for i, val in enumerate(d[6:]):
            quantite = float(str(val).replace(',','.'))
            if not math.isnan(quantite):
                #try:
                    product = Product.objects.get(code_product=f"P{i+1:04d}")
                    item = FactureItem.objects.create(facture=facture,
                                                      product=product,
                                                      quantity=quantite
                                                      )
                    msg += "<p> +item  " + str(item)+" </p>"

                # except Exception as e:
                #     msg += "<p>Erreur " + str(e) + " > " + str(i) + " >>" + str(d[i+6])
                #     continue
        facture.save()
    return msg



@login_required
def import_csv_factures(request):
    def lire_clients(request, csv_reader):
        with open(fichier_csv_clients, 'r', newline='\n') as data:
            csv_reader = csv.DictReader(data, delimiter=',')
            if not "nom" in csv_reader.fieldnames and not "email" in csv_reader.fieldnames:
                m = "Erreur : Le fichier '" + str(fichier_csv_clients) + "'" +" n'a pas de colonne 'nom' ni 'email' (sans espace)"
                return render(request, '', {"liste_tel": str(csv_reader.fieldnames), "message": m})
            m = str(csv_reader.fieldnames)
            m += lire_csv_clients(request, csv_reader)

        m += "Fichier client lu\n"
        return m

    def lire_produits(request, fichier_csv_produits):
        with open(fichier_csv_produits, 'r', newline='\n') as data:
            csv_reader = csv.DictReader(data, delimiter=',')
            if not "nom" in csv_reader.fieldnames and not "code" in csv_reader.fieldnames:
                m = "Erreur : Le fichier '" + str(
                    fichier_csv_produits) + "'" + " n'a pas de colonne 'com' ni 'code' "
                return render(request, 'compta/admin_utils.html',
                              {"liste_tel": str(csv_reader.fieldnames), "message": m})
            m = str(csv_reader.fieldnames)
            m += lire_csv_produits(request, csv_reader)

        m += "Fichier produits lu\n"
        return m

    testIsMembreAsso(request, request.session["asso_slug"])
    form = csvFile_form(request.POST or None, request.FILES or None)
    if form.is_valid():
        m = ""
        try:
            if LOCALL:
                fichier_csv_clients = "/home/eloi/PA_clients.csv"
                fichier_csv_produits = "/home/eloi/PA_produits.csv"
                fichier_csv_factures = "/home/eloi/PA_factures.csv"
            else:
                fichier_csv_clients = request.POST['fichier_csv_clients']
                fichier_csv_produits = request.POST['fichier_csv_produits']
                fichier_csv_factures = request.POST['fichier_csv_factures']


            m += lire_clients(request, fichier_csv_produits)
            m += lire_produits(request, fichier_csv_produits)
            m += lire_csv_factures(request, fichier_csv_factures)
        except Exception as e:
            m+= "<p>ERR " + str(e) + "</p>"

        return render(request, 'compta/admin_utils.html', {"message": m, "title": "Resultat imports factures"})

    return render(request, 'compta/admin_utils.html', {"form": form, "title": "Lancer imports factures"})
