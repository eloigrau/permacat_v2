
from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, HttpResponseRedirect

from django.http import HttpResponseForbidden
import csv
from django.db.models import BooleanField, ExpressionWrapper, Q
from urllib import parse
from blog.models import Projet
from .forms import (Contact_form, Contact_update_form, ContactContact_form,
                    ListeTel_form, csvFile_form, csvText_form, ProjetPhoning_form)

from .models import Adherent, Contact, ContactContact, ProjetPhoning
from bourseLibre.models import Adresse, Profil, Asso
from bourseLibre.views import testIsMembreAsso
from .filters import ContactCarteFilter
from actstream.models import Action
from datetime import date, timedelta, datetime

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from actstream import actions, action
from io import StringIO
from django.db.models import Count, Max, Min
import re
from.views import write_csv_data, is_membre_bureau
from django.contrib.auth.decorators import login_required, permission_required

from unidecode import unidecode


def testIsMembreAsso_bool(request, asso):
    if asso == "public":
        return Asso.objects.get(nom="Public")

    assos = Asso.objects.filter(Q(nom=asso) | Q(slug=asso))
    if assos:
        assos = assos[0]

        if not assos.is_membre(request.user) and not request.user.is_superuser:
            return None
        return assos

    return None

class Contact_ajouter(UserPassesTestMixin, CreateView, ):
    model = Contact
    template_name_suffix = '_ajouter'

    def test_func(self):
        self.asso = testIsMembreAsso_bool(self.request, self.kwargs['asso_slug'])
        if not self.asso:
            return False
        return is_membre_bureau(self.request.user, self.asso.slug) or self.request.user == self.object.profil

    def get_form(self):
        return Contact_form(**self.get_form_kwargs())

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.projet = get_object_or_404(ProjetPhoning, pk=self.request.session["projet_courant_pk"])
        self.object.adresse=Adresse.objects.create(rue=form.cleaned_data['rue'],
                                                   commune=form.cleaned_data['commune'],
                                                   code_postal=form.cleaned_data['code_postal'],
                                                   telephone=form.cleaned_data['telephone'])

        self.object.save()
        #action.send(self.request.user, verb='jardins_nouveau_jp', action_object=self.object, url=self.object.get_absolute_url(),
        #             description="a ajouté le Jardin: '%s'" % self.object.titre)

        return redirect("adherents:phoning_projet_courant", kwargs={'asso_slug': self.asso.slug})


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        self.projet = ProjetPhoning.objects.get(pk=self.request.session['projet_courant_pk'])
        context['projetphoning'] = self.projet
        context['asso_slug'] = self.asso.slug
        return context

class Contact_modifier(UserPassesTestMixin, UpdateView, ):
    model = Contact
    template_name_suffix = '_modifier'

    def test_func(self):
        self.asso = testIsMembreAsso_bool(self.request, self.kwargs['asso_slug'])
        if not self.asso:
            return False
        return is_membre_bureau(self.request.user, self.asso.slug) or self.request.user == self.object.profil

    def get_form(self):
        return Contact_update_form(**self.get_form_kwargs())

    def get_initial(self):
        contact = Contact.objects.get(pk=self.kwargs["pk"])
        if contact.adresse:
            return {
                'rue': contact.adresse.rue,
                'commune': contact.adresse.commune,
                'code_postal': contact.adresse.code_postal,
                'telephone': contact.adresse.telephone,
            }
        return {
            }

    def form_valid(self, form):
        self.object = form.save()
        if not self.object.adresse:
            self.object.adresse = Adresse.objects.create()
        self.object.adresse.rue=form.cleaned_data['rue']
        self.object.adresse.commune=form.cleaned_data['commune']
        self.object.adresse.code_postal=form.cleaned_data['code_postal']
        self.object.adresse.telephone=form.cleaned_data['telephone']
        self.object.adresse.save(recalc=True)
        self.object.save(update_fields=['adresse'])
        #action.send(self.request.user, verb='jardins_nouveau_jp', action_object=self.object, url=self.object.get_absolute_url(),
        #             description="a ajouté le Jardin: '%s'" % self.object.titre)

        if "next" in self.request.GET:
            return redirect(self.request.GET["next"])
        return redirect("adherents:phoning_projet_courant", asso_slug=self.asso.slug)
    # def form_valid(self, form):
    #     desc = " a modifié l'adhérent : " + str(self.object.nom) + ", " + str(self.object.prenom)+ " (" + str(
    #         form.changed_data) + ")"
    #     action.send(self.request.user, verb='adherent_conf66_modifier', action_object=self.object,
    #                 url=self.object.get_absolute_url(), description=desc)
    #     titre = "[PCAT_adherents] Modification de l'adherent : " + str(self.object)
    #     action.send(self.request.user, verb='emails', url=self.object.get_absolute_url(), titre=titre, message=str(self.request.user) + desc, emails=['confederationcontactne66@gmail.com', ])
    #     return super().form_valid(form)

    def get_success_url(self):
        return self.object.get_absolute_url()


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context

class Contact_supprimer(UserPassesTestMixin, DeleteView, ):
    model = Contact
    template_name_suffix = '_supprimer'

    def test_func(self):
        self.asso = testIsMembreAsso_bool(self.request, self.kwargs['asso_slug'])
        if not self.asso:
            return False
        return is_membre_bureau(self.request.user, self.asso.slug) or self.request.user == self.object.profil

    def get_success_url(self):
        #desc = " a supprimé l'adhérent : " + str(self.object.nom) + ", " + str(self.object.prenom)
        #action.send(self.request.user, verb='adherent_conf66_supprimer', url=reverse('adherents:accueil'), description=desc)
        return reverse('adherents:phoning_projet_courant', kwargs={'asso_slug': self.asso.slug})


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context

@login_required
def contact_supprimer(request, asso_slug, contact_pk):
    #if not request.user.has_perm(request.session["request.session.asso_slug"].slug + '_delete_contact'):

    asso = testIsMembreAsso(request, asso_slug)
    contact = get_object_or_404(Contact, pk=contact_pk)
    contact.adresse.delete()
    contact.delete()
    return redirect('adherents:phoning_projet_courant', asso_slug=asso_slug)

class Contact_liste(UserPassesTestMixin, ListView):
    model = Contact
    context_object_name = "contacts"
    template_name_simple = "adherents/carte_contacts_simple.html"
    template_name_complet = "adherents/carte_contacts.html"

    def test_func(self):
        self.asso = testIsMembreAsso_bool(self.request, self.kwargs['asso_slug'])
        if not self.asso:
            return False
        return True

    def get_queryset(self):
        params = dict(self.request.GET.items())
        if 'projet_pk' in self.kwargs:
            self.projet = get_object_or_404(ProjetPhoning, pk=self.kwargs.get('projet_pk'))
            self.request.session["projet_courant_pk"] = self.projet.pk
            self.request.session["projet_phoning_nom"] = self.projet.titre
            self.request.session["asso_slug"] = self.projet.asso.slug
        else:
            if 'projet_courant_pk' in self.request.session:
                self.projet = get_object_or_404(ProjetPhoning, pk=self.request.session["projet_courant_pk"])
            else:
                return redirect('phoning_projet_liste', )

        if "lettre" in self.request.GET:
            qs = Contact.objects.filter(projet=self.projet, nom__istartswith=self.request.GET["lettre"]).order_by("nom","prenom","email","adresse__telephone")
        else:
            qs = Contact.objects.filter(projet=self.projet).order_by("nom","prenom","email","adresse__telephone")
        self.filter = ContactCarteFilter(self.request, self.request.GET, queryset=qs)
        self.qs = self.filter.qs.distinct()
        return self.qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        qs = self.qs
        context["projet"] = self.projet
        context['titre'] = "Phoning : %s (%d)" % (str(self.projet), len(qs))
        #filter = ContactCarteFilter(self.request, self.request.GET, qs)
        context["filter"] = self.filter
        context['is_membre_bureau'] = is_membre_bureau(self.request.user)
        context['historique'] = Action.objects.filter(Q(verb__startswith='phoningConf_'))
        context['asso_slug'] = self.asso.slug
        return context

    def get_template_names(self, *args, **kwargs):
        # Check if the request path is the path for a-url in example app
        if (self.request.path == reverse('adherents:phoning_projet_simple', kwargs={'asso_slug': self.asso.slug, 'projet_pk':self.request.session['projet_courant_pk']}) or
                self.request.path == reverse('adherents:phoning_projet_courant', kwargs={'asso_slug': self.asso.slug})) :
            return [self.template_name_simple]  # Return a list that contains "a.html" template name
        return [self.template_name_complet]  # else return "b.html" template name

@login_required
def phoning_projet_courant(request, asso_slug):
    asso = testIsMembreAsso(request, asso_slug)

    if 'projet_courant_pk' in request.session:
        #return redirect('adherents:phoning_projet_simple', projet_pk=request.session['projet_courant_pk'])
        reversed = reverse('adherents:phoning_projet_simple', kwargs={'asso_slug': asso_slug, 'projet_pk':request.session['projet_courant_pk']})  # create a base url

        if request.GET:  # append the remaining parameters
            reversed += '?' + parse.urlencode(request.GET)
        return HttpResponseRedirect(reversed)
    else:
        return redirect('adherents:phoning_projet_liste')

@login_required
def contactContact_supprimer(request, asso_slug, contact_contact_pk):
    #if not request.user.has_perm('delete_contact'):
    #    return render
    asso = testIsMembreAsso(request, asso_slug)

    c = get_object_or_404(ContactContact, pk=contact_contact_pk)
    c.delete()
    return redirect('adherents:phoning_projet_courant', asso_slug=asso_slug)


@login_required
def contactContact_ajouter(request, asso_slug, contact_pk):
    asso = testIsMembreAsso(request, asso_slug)
    p = get_object_or_404(Contact, pk=contact_pk)
    form = ContactContact_form(request.POST or None)
    if form.is_valid():
        contact = form.save(commit=False)
        contact.contact = p
        contact.profil = request.user
        #contact.commentaire = "(" + str(request.user.username) + ") " + contact.commentaire if contact.commentaire else "(" + str(request.user.username) + ") "
        form.save(commit=True)
        if 'next' in request.GET:
            return HttpResponseRedirect(request.GET['next'].replace("%26",'&').replace("'",''))
        else:
            return redirect('adherents:phoning_projet_courant', asso_slug=asso.slug)


    return render(request, 'adherents/contact_contact_ajouter.html', {"form": form, "contact":p, "asso_slug": asso_slug})



@login_required
def contact_ajouter_accueil(request, asso_slug):
    asso = testIsMembreAsso(request, asso_slug)
    return render(request, 'adherents/contact_ajouter_acceuil.html', {"asso_slug": asso_slug})


@login_required
def nettoyer_telephones(request, asso_slug):
    asso = testIsMembreAsso(request, asso_slug)
    m = ""
    for p in Contact.objects.all():
        if p.adresse:
            if p.adresse.rue:
                try:
                    ad = re.split("\d{5}", p.adresse.rue)
                    if len(ad)>1:
                        code = re.findall("\d{5}", p.adresse.rue)[0]
                        p.adresse.rue = ad[0]
                        p.adresse.code_postal=code
                        p.adresse.commune = ad[1]
                        m+= "<p>MAJ " + str(p.adresse) + "</p>"
                except:
                    m+= "<p>pb " + p.adresse.rue + "</p>"
            if p.adresse.telephone:
                if p.adresse.telephone.startswith("6"):
                    p.adresse.telephone = "0" + str(p.adresse.telephone.strip())
                    m += "<p>ajustement06 tel : " + str(p.adresse.telephone) + "</p>"
                elif p.adresse.telephone.startswith("7"):
                    p.adresse.telephone = "0" + str(p.adresse.telephone.strip())
                    m += "<p>ajustement07 tel : " + str(p.adresse.telephone) + "</p>"

                elif p.adresse.telephone.startswith("33"):
                    p.adresse.telephone = "+" + str(p.adresse.telephone.strip())
                    m += "<p>ajustement33 tel : " + str(p.adresse.telephone) + "</p>"

                if len(p.adresse.telephone) < 4:
                    p.commentaire = p.commentaire if p.commentaire else ""
                    p.commentaire +=  " " + str(p.adresse.telephone.strip())
                    p.adresse.telephone = ""
                    m += "<p>petit tel : " + str(p.adresse.telephone.strip()) + "</p>"

                p.adresse.telephone=p.adresse.telephone.replace('/','').replace('.','').replace(' ','').strip()
                p.adresse.save()
                p.save(update_fields=['adresse'])

                if Contact.objects.filter(adresse__telephone=p.adresse.telephone):
                    m += "<p>DOUBLE tel : " + str(p) + "</p>"


    return render(request, 'adherents/contact_ajouter_listetel_res.html', {"message": m, "asso_slug": asso_slug})

@login_required
def supprimer_doublons(request, asso_slug):
    params = dict(request.GET.items())
    if 'tel' in params:
        unique_fields = ['adresse__telephone', ]
    else:
        unique_fields = ['nom', 'prenom', 'adresse__telephone']

    duplicates = (
        Contact.objects.values(*unique_fields)
        .annotate(max_id=Min('id'), count_id=Count('id'))
        .filter(count_id__gt=1)
    )

    for duplicate in duplicates:
        (
            Contact.objects
            .filter(**{x: duplicate[x] for x in unique_fields})
            .exclude(Q(adherent__isnull=False) | Q(id=duplicate['max_id']))
            .delete()
        )


    return render(request, 'adherents/contact_ajouter_listetel_res.html', {"message": str(duplicates), "asso_slug": asso_slug})



def creerContact(projet, telephone, nom=None, prenom=None, email=None, rue=None, commune=None, code_postal=None, adherent=None):
    #if not telephone:
     #   return 0, None

    if not(telephone or nom or prenom or email or code_postal):
        return 0, None

    if Contact.objects.filter(adresse__code_postal=code_postal,
                                 adresse__telephone=telephone,
                                nom=nom,
                                prenom=prenom,
                                projet=projet,
                                email=email).exists():
        if adherent:
            contacts = Contact.objects.filter(adresse__code_postal=code_postal,
                                     adresse__telephone=telephone,
                                    nom=nom,
                                    prenom=prenom,
                                    projet=projet,
                                    email=email)
            for c in contacts:
                c.adherent=adherent
                c.save()
    else:

        if code_postal and telephone:
            adresse, created = Adresse.objects.get_or_create(
                                        telephone=telephone,
                                        commune=commune,
                                        code_postal=code_postal,
                                        rue=rue,
                                        )
        else:
            if telephone or commune or code_postal or rue:
                adresse = Adresse.objects.create(
                                            telephone=telephone,
                                                commune=commune,
                                                code_postal=code_postal,
                                                rue=rue,
                                            )
            else:
                adresse = None
        p, created = Contact.objects.get_or_create(
                                nom=nom,
                                prenom=prenom,
                                email=email,
                                adresse=adresse,
                                adherent=adherent,
                                projet=projet
        )
        return 1, p
    return 0, None


@login_required
def ajouterAdherents(request, asso_slug ):
    testIsMembreAsso(request, asso_slug)
    projet = ProjetPhoning.objects.get(pk=request.session['projet_courant_pk'] )
    adherents = Adherent.objects.filter(asso=projet.asso)
    m = ""
    j = 0
    for i, adherent in enumerate(adherents):
        #if j>5 or i> 200:
         #   break
        res, p = creerContact(projet=projet,
                              telephone=adherent.adresse.telephone,
                             nom=adherent.nom,
                             prenom=adherent.prenom ,
                             email=adherent.email,
                             rue=adherent.adresse.rue,
                             commune=adherent.adresse.commune,
                             code_postal=adherent.adresse.code_postal,
                             adherent=adherent,
                              )
        if res:
            m += "<p>ajout " + str(adherent) +"</p>"
            j += 1
        else:
            m += "<p>refus " + str(adherent) +"</p>"


    return render(request, 'adherents/contact_ajouter_listetel_res.html', {"message": m, "asso_slug": asso_slug})

@login_required
def ajouterMembresGroupe(request, asso_slug ):
    asso = testIsMembreAsso(request, asso_slug)
    request.session['asso_slug'] = asso_slug
    projet = ProjetPhoning.objects.get(pk=request.session['projet_courant_pk'] )
    profils = asso.getProfils()
    m = ""
    j=0
    for i, adherent in enumerate(profils):
        #if j>5 or i> 200:
         #   break
        adh = Adherent.objects.filter(profil=adherent)
        if adh:
            ad = adh[0]
        else:
            ad= None
        res, p = creerContact(projet=projet,
                              telephone=adherent.adresse.telephone,
                             nom=adherent.first_name,
                             prenom=adherent.last_name ,
                             email=adherent.email,
                             rue=adherent.adresse.rue,
                             commune=adherent.adresse.commune,
                             code_postal=adherent.adresse.code_postal,
                             adherent=ad,
                              )
        if res:
            m += "<p>ajout " + str(adherent) +"</p>"
            j += 1
        else:
            m += "<p>refus " + str(adherent) +"</p>"


    return render(request, 'adherents/contact_ajouter_listetel_res.html', {"message": m, "asso_slug": asso_slug})


@login_required
def phoning_contact_ajouter_listetel(request, asso_slug):
    testIsMembreAsso(request, asso_slug)

    projet = ProjetPhoning.objects.get(pk=request.session['projet_courant_pk'] )
    form = ListeTel_form(request.POST or None)
    if form.is_valid():
        tels = form.cleaned_data['telephones']
        m = ""
        for i, tel in enumerate(tels.split(',')):
            if len(tel)<5:
                m += "<p>" + str(i) +" Errlong " + str(tel) +" > " + "</p>"
                continue
            try:
                res, p = creerContact(projet=projet, telephone=str(tel))
                if res:
                    m += "<p>" + str(i) +" ajout " + str(p) +"</p>"
                else:
                    m += "<p>" + str(i) +" refus " + str(tel) +"</p>"
            except Exception as e:
                m += "<p>" + str(i) +" erreur " + str(tel) +" > " + str(e) + "</p>"

        return render(request, 'adherents/contact_ajouter_listetel_res.html', {"liste_tel": tels, "message": m})

    return render(request, 'adherents/contact_ajouter_listetel.html', {"form": form, "asso_slug": asso_slug})



@login_required
def lireTableauContact(request, asso_slug, csv_reader):
    testIsMembreAsso(request, asso_slug)
    projet_courant = ProjetPhoning.objects.get(pk=request.session['projet_courant_pk'] )
    #if not request.user.has_perm('add_contact'):
   #     return HttpResponseForbidden()
    msg = ""
    for i, line in enumerate(csv_reader):
        #if i == 0:
        #    continue
        try:
            cles = line.keys()
            if "telephone" in line and line["telephone"] and Adresse.objects.filter(telephone__iexact=line["telephone"]):
                msg += "<p> DEJA tel " + str(line) + "#" + line["telephone"] +"#</p>"
                continue
            if "email" in line and line["email"] and Adresse.objects.filter(telephone__iexact=line["email"]):
                msg += "<p> DEJA mail " + str(line) + "#" + line["email"] +"#</p>"
                continue
            #if not line["telephone"] :
            #    msg += "<p> pas de tel " + str(line) + "</p>"
            #    continue
            if ("rue" in line and line["rue"]) or ("code_postal" in line and line["code_postal"]) or ("commune" in line and line["commune"]) or ("telephone" in line and line["telephone"]):
                adres, created = Adresse.objects.get_or_create(rue=line["rue"] if 'rue' in cles else "",
                                                               code_postal=line["code_postal"] if 'code_postal' in cles else "",
                                                               commune=line["commune"] if 'commune' in cles else "",
                                                               telephone=line["telephone"] if 'telephone' in cles else "")
                adres.save()
            else:
                adres, created = Adresse.objects.get_or_create(rue="adresse inconnue")

            contact, created = Contact.objects.get_or_create(
                nom=line["nom"] if 'nom' in cles else "",
                prenom=line["prenom"] if 'prenom' in cles else "",
                adresse=adres,
                email=line["email"] if 'email' in cles else "",
                commentaire=line["commentaire"] if 'commentaire' in cles else "",
                projet=projet_courant
            )
            if created:
                msg += "<p> ajoute adherent " + str(line) + " / " + str(contact) + "</p>"
            else:
                msg += "<p>  adherent  deja present " + str(line) + " / " + str(contact) + "</p>"

        except Exception as e:
            msg += "<p>Erreur " + str(e) + " > " + str(i) + " " + str(line)
    return msg


@login_required
def phoning_contact_ajouter_csv(request, asso_slug, ):

    testIsMembreAsso(request, asso_slug)
    #if not request.user.has_perm('add_contact'):
    #    return HttpResponseForbidden()
    form = csvText_form(request.POST or None)
    if form.is_valid():
        texte_csv = form.cleaned_data['texte_csv']
        msg = "import texte_csv : "
        csv_reader = csv.DictReader(StringIO(texte_csv))
        if not "telephone" in csv_reader.fieldnames and not "email" in csv_reader.fieldnames:
            m = "Erreur : Le fichier '" + str(texte_csv) + "'" +" n'a pas de colonne 'telephone' ni 'email' (sans espace)"
            return render(request, 'adherents/contact_ajouter_listetel_res.html', {"liste_tel": str(csv_reader.fieldnames), "message": m})

        m = lireTableauContact(request, asso_slug, csv_reader)
        return render(request, 'adherents/contact_ajouter_listetel_res.html', {"liste_tel": str(csv_reader), "message": m})

    return render(request, 'adherents/contact_ajouter_csv1.html', {"form": form, "asso_slug": asso_slug})


@login_required
def phoning_contact_ajouter_csv_viti(request, asso_slug):

    testIsMembreAsso(request, asso_slug)
    #if not request.user.has_perm('add_contact'):
    #    return HttpResponseForbidden()
    form = csvText_form(request.POST or None)
    if form.is_valid():
        texte_csv = form.cleaned_data['texte_csv']
        m = "import texte_csv : "
        csv_reader = csv.DictReader(StringIO(texte_csv))
        if not "telephone" in csv_reader.fieldnames and not "email" in csv_reader.fieldnames:
            m += "Erreur : Le fichier '" + str(texte_csv) + "'" +" n'a pas de colonne 'telephone' ni 'email' (sans espace)"
            return render(request, 'adherents/contact_ajouter_listetel_res.html', {"liste_tel": str(csv_reader.fieldnames), "message": m})

        for i, line in enumerate(csv_reader):
            try:
                if line["telephone"] :
                    contacts = Contact.objects.filter(adresse__telephone__iexact=line["telephone"].replace('/', '').replace('.', '').replace(' ','').strip())
                    if len(contacts) >1:
                        m += "doublon: " + str(line)
                    elif len(contacts) == 1:
                        if not contacts[0].commentaire or not "Viti CP" in contacts[0].commentaire:
                            contacts[0].commentaire = contacts[0].commentaire  + " - Viti CP" if contacts[0].commentaire else "Viti CP"
                            contacts[0].save()
                        m += " ajout Viti" + str(i)
                    else:
                        m += "pas ajout Viti" + str(i) + " "+ str(line["telephone"])

                else:
                    m += "pas tel Viti" + str(i) + " "+ str(line["telephone"])


            except Exception as e:
                m += "<p>Erreur " + str(e) + " > " + str(i) + " " + str(line)
        return render(request, 'adherents/contact_ajouter_listetel_res.html', {"liste_tel": str(csv_reader), "message": m})

    return render(request, 'adherents/contact_ajouter_csv1.html', {"form": form, "asso_slug": asso_slug})

@login_required
def phoning_contact_ajouter_csv_inversernomprenom(request, asso_slug):

    testIsMembreAsso(request, asso_slug)
    #if not request.user.has_perm('add_contact'):
    #    return HttpResponseForbidden()
    form = csvText_form(request.POST or None)
    if form.is_valid():
        texte_csv = form.cleaned_data['texte_csv']
        m = "import texte_csv : "
        csv_reader = csv.DictReader(StringIO(texte_csv))
        if not "telephone" in csv_reader.fieldnames and not "email" in csv_reader.fieldnames:
            m = "Erreur : Le fichier '" + str(texte_csv) + "'" +" n'a pas de colonne 'telephone' ni 'email' (sans espace)"
            return render(request, 'adherents/contact_ajouter_listetel_res.html', {"liste_tel": str(csv_reader.fieldnames), "message": m})

        for i, line in enumerate(csv_reader):
            try:
                if line["telephone"] and line["nom"]:
                    for cont in Contact.objects.filter(adresse__telephone__iexact=line["telephone"].replace('/','').replace('.','').replace(' ','').strip()):
                        if line["nom"] == cont.prenom:
                            cont.nom = line["nom"]
                            cont.prenom = line["prenom"]
                            cont.adresse.commune = line["commune"]
                            cont.save()
                            m += "modif" + str(cont)

            except Exception as e:
                m += "<p>Erreur " + str(e) + " > " + str(i) + " " + str(line)

        return render(request, 'adherents/contact_ajouter_listetel_res.html', {"liste_tel": str(csv_reader), "message": m})

    return render(request, 'adherents/contact_ajouter_csv1.html', {"form": form, "asso_slug": asso_slug})

@login_required
def phoning_contact_ajouter_csv_editNonVotants(request, asso_slug,):

    testIsMembreAsso(request, asso_slug)
    #if not request.user.has_perm('add_contact'):
    #    return HttpResponseForbidden()
    form = csvText_form(request.POST or None)
    if form.is_valid():
        texte_csv = form.cleaned_data['texte_csv']
        msg = "import texte_csv : "
        csv_reader = csv.DictReader(StringIO(texte_csv))
        j =0
        for i, line in enumerate(csv_reader):
            try:
                if line["NOM_PATRONYMIQUE"]:
                    try:
                        for cont in Contact.objects.filter(nom=line["NOM_PATRONYMIQUE"], prenom=line["PRENOMS"].split(' ')[0]):
                            if not cont.commentaire or not "Votant" in cont.commentaire:
                                if cont.adresse:
                                    cont.adresse.commune = line["LIBELLE_COMMUNE_RESIDENCE"]
                                    cont.adresse.code_postal = line["CODE_POSTAL_RESIDENCE"]
                                    cont.adresse.rue = line["ADRESSE1"] + " " + line["ADRESSE2"]
                                    cont.adresse.save(recalc=True)
                                cont.commentaire = "Votant Vérifié "+ cont.commentaire if cont.commentaire else "Votant Vérifié"
                                cont.save()
                                j += 1
                    except:
                        for cont in Contact.objects.filter(nom=line["NOM_PATRONYMIQUE"], prenom=line["PRENOMS"]):
                            if not cont.commentaire or not "Votant" in cont.commentaire:
                                if cont.adresse:
                                    cont.adresse.commune = line["LIBELLE_COMMUNE_RESIDENCE"]
                                    cont.adresse.code_postal = line["CODE_POSTAL_RESIDENCE"]
                                    cont.adresse.rue = line["ADRESSE1"] + " " + line["ADRESSE2"]
                                    cont.adresse.save(recalc=True)
                                cont.commentaire = "Votant Vérifié "+ cont.commentaire if cont.commentaire else "Votant Vérifié"
                                cont.save()
                                j += 1

            except Exception as e:
                msg += "<p>Erreur " + str(e) + " > " + str(i) + " " + str(line)
        msg += "nbModifs :" + str(j)
        return render(request, 'adherents/contact_ajouter_listetel_res.html', {"liste_tel": str(csv_reader), "message": msg})

    return render(request, 'adherents/contact_ajouter_csv1.html', {"form": form, "asso_slug": asso_slug})



@login_required
def phoning_contact_ajouter_csv2(request, asso_slug):
    testIsMembreAsso(request, asso_slug)
    form = csvFile_form(request.POST or None, request.FILE or None)
    if form.is_valid():
        fichier = request.FILES['fichier_csv']
        with open(fichier, 'r', newline='\n') as data:
            csv_reader = csv.DictReader(data, delimiter=',')
            if not "telephone" in csv_reader.fieldnames and not "email" in csv_reader.fieldnames:
                m = "Erreur : Le fichier '" + str(fichier) + "'" +" n'a pas de colonne 'telephone' ni 'email' (sans espace)"
                return render(request, 'adherents/contact_ajouter_listetel_res.html', {"liste_tel": str(csv_reader.fieldnames), "message": m})
            m = str(csv_reader.fieldnames)
            m += lireTableauContact(request, asso_slug, csv_reader)
        return render(request, 'adherents/contact_ajouter_listetel_res.html', {"liste_tel": str(csv_reader), "message": m})

    return render(request, 'adherents/contact_ajouter_csv2.html', {"form": form, "asso_slug": asso_slug})



@login_required
def import_adherents_ggl(request, asso_slug):
    if not is_membre_bureau(request.user, asso_slug):
        return HttpResponseForbidden()
    params = dict(request.GET.items())
    # fic = params["fic"]
    msg =""

    return render(request, "adherents/accueil_admin.html", {"msg":msg})


@login_required
def get_csv_contacts(request, asso_slug):
    """A view that streams a large CSV file."""
    if not is_membre_bureau(request.user, asso_slug):
        return HttpResponseForbidden()
    profils = Contact.objects.filter(projet__pk=request.session["projet_courant_pk"]).order_by("nom","prenom","email")
    profils_filtres = ContactCarteFilter(request, request.GET, queryset=profils)
    #current_year = date.today().isocalendar()[0]

    csv_data = [("nom","prenom","telephone","email","adresse_postale","code_postal","commune","adherent_nom","commentaire",),]
    csv_data += [(a.nom, a.prenom, a.adresse.telephone if a.adresse else "", a.email,a.adresse.rue if a.adresse else "",a.adresse.code_postal if a.adresse else "",a.adresse.commune if a.adresse else "", a.get_profil_username(), a.commentaire)
                 for a in profils_filtres.qs.distinct() ]

    return write_csv_data(request, csv_data)



def ajax_projet(request, asso_slug):
    testIsMembreAsso(request, asso_slug)
    try:
        asso_slug = request.GET.get('asso_slug')
        projets = ProjetPhoning.objects.filter(asso__slug=asso_slug)

        return render(request, 'adherents/ajax/projets_dropdown_list_options.html',
                      {'listeProjets':projets})
    except:
        return render(request, 'blog/ajax/projets_dropdown_list_options.html', {'categories':"",} )


class ProjetPhoning_ajouter(UserPassesTestMixin, CreateView):
    model = ProjetPhoning
    template_name_suffix = '_ajouter'

    def test_func(self):
        self.asso = testIsMembreAsso_bool(self.request, self.kwargs['asso_slug'])
        if not self.asso:
            return False
        return is_membre_bureau(self.request.user, self.asso.slug)

    def get_form(self):
        return ProjetPhoning_form(self.request, **self.get_form_kwargs())

    def form_valid(self, form):
        self.object = form.save()
        #action.send(self.request.user, verb='jardins_nouveau_jp', action_object=self.object, url=self.object.get_absolute_url(),
        #             description="a ajouté le Jardin: '%s'" % self.object.titre)

        return redirect(self.object)

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context


class ProjetPhoning_modifier(UserPassesTestMixin, UpdateView):
    model = ProjetPhoning
    template_name_suffix = '_modifier'

    def test_func(self):
        self.asso = testIsMembreAsso_bool(self.request, self.kwargs['asso_slug'])
        if not self.asso:
            return False
        return is_membre_bureau(self.request.user, self.asso.slug)

    def get_form(self):
        return ProjetPhoning_form(self.request, **self.get_form_kwargs())

    def form_valid(self, form):
        self.object = form.save()
        return redirect(self.get_success_url())

    def get_success_url(self):
        return self.object.get_absolute_url()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context


class ProjetPhoning_supprimer(UserPassesTestMixin, DeleteView, ):
    model = ProjetPhoning
    template_name_suffix = '_supprimer'

    def test_func(self):
        self.asso = testIsMembreAsso_bool(self.request, self.kwargs['asso_slug'])
        if not self.asso:
            return False
        return is_membre_bureau(self.request.user, self.asso.slug)

    def get_success_url(self):
        return reverse('adherents:phoning_projet_courant', {"asso_slug":self.asso.slug})


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['asso_slug'] = self.asso.slug
        return context

class ProjetPhoning_liste(UserPassesTestMixin, ListView):
    model = ProjetPhoning
    context_object_name = "projets"
    template_name = "adherents/projetphoning_list.html"

    def test_func(self):
        self.asso = testIsMembreAsso_bool(self.request, self.kwargs['asso_slug'])
        if not self.asso:
            return False
        return is_membre_bureau(self.request.user, self.asso.slug)

    def get_queryset(self):
        params = dict(self.request.GET.items())
        if 'asso' in params:
            self.request.session["asso_slug"] = params['asso']
            self.qs = ProjetPhoning.objects.filter(asso__slug=params['asso'])
        elif 'tous' in params:
            self.qs = ProjetPhoning.objects.filter(asso__slug__in=self.request.user.getListeSlugsAssos())
        elif "asso_slug" in self.request.session:
            self.qs = ProjetPhoning.objects.filter(asso__slug=self.request.session["asso_slug"])
        else:
            self.qs = ProjetPhoning.objects.filter(asso__slug__in=self.request.user.getListeSlugsAssos())
        return self.qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['asso_list'] = [(x.slug, x.nom,) for x in Asso.objects.all().order_by("id") if
                                self.request.user.est_autorise(x.slug)]
        context["asso_slug"] = self.asso.slug

        #context["filter"] = filter
        return context



@login_required
def nettoyer_noms(request, asso_slug):
    testIsMembreAsso(request, asso_slug)
    m = ""
    for p in Contact.objects.filter(projet__asso__slug="conf66"):
        if p.nom:
            try:
                p.nom = p.nom.replace("é","e").replace("è","e").replace("É","E").replace("È","E").upper()
                p.prenom = p.prenom.replace("é","e").replace("è","e").replace("É","E").replace("È","E").upper()
                p.save()
            except Exception as e:
                m+= "erreur : "+str(e)

    return render(request, 'adherents/contact_ajouter_listetel_res.html', {"message": m})



@login_required
def ajax_infocontact(request, asso_slug, pk):
    testIsMembreAsso(request, asso_slug)

    projet = get_object_or_404(ProjetPhoning, pk=pk)
    contacts = Contact.objects.filter(projet=projet)
    contact_contacts = ContactContact.objects.filter(contact__in=contacts)
    nb_total = contacts.count()
    nb_contacts_total = contact_contacts.count()
    nb_contactes = contacts.annotate(num_b=Count('contactcontact')).filter(num_b__gt=0).count()
    nb_contactes_ok = contacts.filter(contactcontact__statut="0").annotate(num_b=Count('contactcontact')).filter(num_b__gt=0).count()
    nb_contactes_pasok  = contacts.filter(Q(contactcontact__statut="0") | Q(contactcontact__statut="1")| Q(contactcontact__statut="2")| Q(contactcontact__statut="3")| Q(contactcontact__statut="4")).annotate(num_b=Count('contactcontact')).filter(num_b__gt=0).count()
    return render(request, 'adherents/ajax/nb_contacts.html',
                  {
                      'nb_total':nb_total,
                      'nb_contacts_total':nb_contacts_total,
                      'nb_contactes':nb_contactes,
                      'nb_contactes_ok':nb_contactes_ok,
                      'nb_contactes_pasok':nb_contactes_pasok
                  })

