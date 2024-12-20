
from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView, UpdateView, DeleteView, CreateView, DetailView
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, HttpResponseRedirect

from django.http import HttpResponseForbidden
import csv
from django.db.models import Q

from blog.models import Projet
from .forms import (Contact_form, Contact_update_form, ContactContact_form,
                    ListeTel_form, csvFile_form, csvText_form, ProjetPhoning_form)

from .models import Adherent, Contact, ContactContact, ProjetPhoning
from bourseLibre.models import Adresse, Profil, Asso
from .filters import ContactCarteFilter
from actstream.models import Action
from datetime import date, timedelta, datetime

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from actstream import actions, action
from io import StringIO
from django.db.models import Count, Max
import re
from.views import write_csv_data, is_membre_bureau
from django.contrib.auth.decorators import login_required, permission_required

class Contact_ajouter(CreateView):
    model = Contact
    template_name_suffix = '_ajouter'

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

        return redirect("adherents:phoning_projet_courant")


    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        self.projet = ProjetPhoning.objects.get(pk=self.request.session['projet_courant_pk'])
        context['projetphoning'] = self.projet
        return context

class Contact_modifier(UpdateView, UserPassesTestMixin):
    model = Contact
    template_name_suffix = '_modifier'

    def test_func(self):
        return self.request.user.has_perm(self.object.asso.abreviation + '_add_contact')

    def get_form(self):
        self.projet = ProjetPhoning.objects.get(pk=self.kwargs["pk"])
        return Contact_update_form(**self.get_form_kwargs())

    def get_initial(self):
        contact = Contact.objects.get(pk=self.kwargs["pk"])
        return {
            'rue': contact.adresse.rue,
            'commune': contact.adresse.commune,
            'code_postal': contact.adresse.code_postal,
            'telephone': contact.adresse.telephone,
        }

    def form_valid(self, form):
        self.object = form.save()
        self.object.adresse.rue=form.cleaned_data['rue']
        self.object.adresse.commune=form.cleaned_data['commune']
        self.object.adresse.code_postal=form.cleaned_data['code_postal']
        self.object.adresse.telephone=form.cleaned_data['telephone']
        self.object.adresse.save(recalc=True)
        self.object.save(update_fields=['adresse'])
        #action.send(self.request.user, verb='jardins_nouveau_jp', action_object=self.object, url=self.object.get_absolute_url(),
        #             description="a ajouté le Jardin: '%s'" % self.object.titre)

        return redirect("adherents:phoning_projet_courant")
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


class Contact_supprimer(UserPassesTestMixin, DeleteView, ):
    model = Contact
    template_name_suffix = '_supprimer'

    def test_func(self):
        return self.request.user.has_perm(self.object.asso.abreviation + '_delete_contact')

    def get_success_url(self):
        #desc = " a supprimé l'adhérent : " + str(self.object.nom) + ", " + str(self.object.prenom)
        #action.send(self.request.user, verb='adherent_conf66_supprimer', url=reverse('adherents:accueil'), description=desc)
        return reverse('adherents:phoning_projet_courant')


@login_required
def contact_supprimer(request, contact_pk):
    if not request.user.has_perm(request.session["asso_courante"].abreviation + '_delete_contact'):
        return HttpResponseForbidden()
    contact = get_object_or_404(Contact, pk=contact_pk)
    contact.adresse.delete()
    contact.delete()
    return redirect('adherents:phoning_projet_courant')

class Contact_liste(ListView, UserPassesTestMixin):
    model = Contact
    context_object_name = "contacts"
    template_name_simple = "adherents/carte_contacts_simple.html"
    template_name_complet = "adherents/carte_contacts.html"

    def test_func(self):
        return self.request.user.has_perm(self.object.asso.abreviation + '_liste_contact')

    def get_queryset(self):
        params = dict(self.request.GET.items())
        if 'projet_pk' in self.kwargs:
            self.projet = get_object_or_404(ProjetPhoning, pk=self.kwargs.get('projet_pk'))
            self.request.session["projet_courant_pk"] = self.projet.pk
            self.request.session["projet_phoning_nom"] = self.projet.titre
        else:
             self.projet = get_object_or_404(ProjetPhoning, pk= self.request.session["projet_courant_pk"])

        if "lettre" in self.request.GET:
            qs = Contact.objects.filter(projet=self.projet, nom__istartswith=self.request.GET["lettre"]).order_by("nom","prenom","email","adresse__telephone")
        else:
            qs = Contact.objects.filter(projet=self.projet).order_by("nom","prenom","email","adresse__telephone")
        profils_filtres = ContactCarteFilter(self.request.GET, queryset=qs)
        self.qs = profils_filtres.qs.distinct()
        return self.qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        qs = self.qs
        context["projet"] = self.projet
        context['titre'] = "Phoning : %s (%d)" % (str(self.projet), len(qs))
        filter = ContactCarteFilter(self.request.GET, qs)
        context["filter"] = filter
        context['is_membre_bureau'] = is_membre_bureau(self.request.user)
        context['historique'] = Action.objects.filter(Q(verb__startswith='phoningConf_'))
        return context

    def get_template_names(self, *args, **kwargs):
        # Check if the request path is the path for a-url in example app
        if self.request.path == reverse('adherents:phoning_projet_simple', kwargs={'projet_pk':self.request.session['projet_courant_pk']}) or self.request.path == reverse('adherents:phoning_projet_courant') :
            return [self.template_name_simple]  # Return a list that contains "a.html" template name
        return [self.template_name_complet]  # else return "b.html" template name

@login_required
def phoning_projet_courant(request):
    if 'projet_courant_pk' in request.session:
        return redirect('adherents:phoning_projet_simple', projet_pk=request.session['projet_courant_pk'])
    else:
        return redirect('adherents:phoning_projet_liste',)



@login_required
def contactContact_supprimer(request, contact_contact_pk):
    if not request.user.has_perm('delete_contact'):
        return render
    c = get_object_or_404(ContactContact, pk=contact_contact_pk)
    c.delete()
    return redirect('adherents:phoning_projet_courant')

@login_required
def contactContact_ajouter(request, contact_pk):
    p = get_object_or_404(Contact, pk=contact_pk)
    form = ContactContact_form(request.POST or None)
    if form.is_valid():
        contact = form.save(commit=False)
        contact.contact = p
        form.save(commit=True)
        return redirect('adherents:phoning_projet_courant')

    return render(request, 'adherents/contact_contact_ajouter.html', {"form": form, "contact":p})



@login_required
def contact_ajouter_accueil(request):
    return render(request, 'adherents/contact_ajouter_acceuil.html', {})


@login_required
def nettoyer_telephones(request):
    m = ""
    for p in Contact.objects.all():
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
                p.commentaire = p.commentaire if p.commentaire else "" + " " + str(p.adresse.telephone.strip())
                p.adresse.telephone = ""
                m += "<p>petit tel : " + str(p.adresse.telephone.strip()) + "</p>"

            p.adresse.telephone=p.adresse.telephone.replace('/','').replace('.','').replace(' ','').strip()
            p.adresse.save()
            p.save(update_fields=['adresse'])

            if Contact.objects.filter(adresse__telephone=p.adresse.telephone):
                m += "<p>DOUBLE tel : " + str(p) + "</p>"


    return render(request, 'adherents/contact_ajouter_listetel_res.html', {"message": m})


@login_required
def supprimer_doublons(request):
    params = dict(request.GET.items())
    if 'tel' in params:
        unique_fields = ['adresse__telephone', ]
    else:
        unique_fields = ['nom', 'prenom', 'adresse__telephone']

    duplicates = (
        Contact.objects.values(*unique_fields)
        .order_by('nom')
        .annotate(max_id=Max('id'), count_id=Count('id'))
        .filter(count_id__gt=1)
    )

    for duplicate in duplicates:
        (
            Contact.objects
            .filter(**{x: duplicate[x] for x in unique_fields})
            .exclude(id=duplicate['max_id'])
            .delete()
        )


    return redirect('adherents:phoning_projet_courant')


def creerContact(projet, telephone, nom=None, prenom=None, email=None, rue=None, commune=None, code_postal=None, adherent=None):
    #if not telephone:
     #   return 0, None

    if not(telephone or nom or prenom or email or code_postal) or (adherent and Contact.objects.filter(adherent=adherent).exists()):
        return 0, None

    if not Contact.objects.filter(adresse__code_postal=code_postal,
                                 adresse__telephone=telephone,
                                nom=nom,
                                prenom=prenom,
                                projet=projet,
                                email=email).exists():

        if code_postal and telephone:
            adresse, created = Adresse.objects.get_or_create(
                                        telephone=telephone,
                                        commune=commune,
                                        code_postal=code_postal,
                                        rue=rue,
                                        )
        else:
            adresse = Adresse.objects.create(
                                        telephone=telephone,
                                            commune=commune,
                                            code_postal=code_postal,
                                            rue=rue,
                                        )
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
def ajouterAdherents(request):
    projet = ProjetPhoning.objects.get(pk=request.session['projet_courant_pk'] )
    adherents = Adherent.objects.filter(asso=projet.asso)
    m = ""
    j=0
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


    return render(request, 'adherents/contact_ajouter_listetel_res.html', {"message": m})


@login_required
def phoning_contact_ajouter_listetel(request):

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

    return render(request, 'adherents/contact_ajouter_listetel.html', {"form": form})



def lireTableauContact(request, csv_reader):
    projet_courant = ProjetPhoning.objects.get(pk=request.session['projet_courant_pk'] )
    if not request.user.has_perm('add_contact'):
        return HttpResponseForbidden()
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
def phoning_contact_ajouter_csv(request,):
    if not request.user.has_perm('add_contact'):
        return HttpResponseForbidden()
    form = csvText_form(request.POST or None)
    if form.is_valid():
        texte_csv = form.cleaned_data['texte_csv']
        msg = "import texte_csv : "
        csv_reader = csv.DictReader(StringIO(texte_csv))
        if not "telephone" in csv_reader.fieldnames:
            m = "Erreur : Le fichier '" + str(texte_csv) + "'" +" n'a pas de colonne 'telephone'"
            return render(request, 'adherents/contact_ajouter_listetel_res.html', {"liste_tel": str(csv_reader.fieldnames), "message": m})

        m = lireTableauContact(request, csv_reader)
        return render(request, 'adherents/contact_ajouter_listetel_res.html', {"liste_tel": str(csv_reader), "message": m})

    return render(request, 'adherents/contact_ajouter_csv1.html', {"form": form})



@login_required
def phoning_contact_ajouter_csv2(request):
    form = csvFile_form(request.POST or None, request.FILE or None)
    if form.is_valid():
        fichier = request.FILES['fichier_csv']
        msg = "import adherents_fic : " + fichier
        with open(fichier, 'r', newline='\n') as data:
            csv_reader = csv.DictReader(data, delimiter=',')
            if not "telephone" in csv_reader.fieldnames:
                m = "Erreur : Le fichier '" + str(fichier) + "'" +" n'a pas de colonne 'telephone'"
                return render(request, 'adherents/contact_ajouter_listetel_res.html', {"liste_tel": str(csv_reader.fieldnames), "message": m})

            m = lireTableauContact(request, csv_reader)
        return render(request, 'adherents/contact_ajouter_listetel_res.html', {"liste_tel": str(csv_reader), "message": m})

    return render(request, 'adherents/contact_ajouter_csv2.html', {"form": form})



@login_required
def import_adherents_ggl(request):
    params = dict(request.GET.items())
    # fic = params["fic"]
    msg =""

    return render(request, "adherents/accueil_admin.html", {"msg":msg})


@login_required
def get_csv_contacts(request):
    """A view that streams a large CSV file."""
    profils = Contact.objects.filter(projet__pk=request.session["projet_courant_pk"]).order_by("nom","prenom","email")
    profils_filtres = ContactCarteFilter(request.GET, queryset=profils)
    #current_year = date.today().isocalendar()[0]

    csv_data = [("nom","prenom","telephone","email","adresse_postale","code_postal","commune","adherent_nom","commentaire",),]
    csv_data += [(a.nom, a.prenom, a.adresse.telephone, a.email,a.adresse.rue,a.adresse.code_postal,a.adresse.commune, a.get_profil_username(), a.commentaire)
                 for a in profils_filtres.qs.distinct() ]

    return write_csv_data(request, csv_data)



def ajax_projet(request):
    try:
        asso_abreviation = request.GET.get('asso_abreviation')
        projets = ProjetPhoning.objects.filter(asso__abreviation=asso_abreviation)

        return render(request, 'adherents/ajax/projets_dropdown_list_options.html',
                      {'listeProjets':projets})
    except:
        return render(request, 'blog/ajax/projets_dropdown_list_options.html', {'categories':"",} )


class ProjetPhoning_ajouter(CreateView, UserPassesTestMixin):
    model = ProjetPhoning
    template_name_suffix = '_ajouter'

    def test_func(self):
        return self.request.user.has_perm(self.object.asso.abreviation + '_add_projetphoning')

    def get_form(self):
        return ProjetPhoning_form(**self.get_form_kwargs())

    def form_valid(self, form):
        self.object = form.save()
        #action.send(self.request.user, verb='jardins_nouveau_jp', action_object=self.object, url=self.object.get_absolute_url(),
        #             description="a ajouté le Jardin: '%s'" % self.object.titre)

        return redirect(self.object)



class ProjetPhoning_modifier(UpdateView, UserPassesTestMixin):
    model = ProjetPhoning
    template_name_suffix = '_modifier'

    def test_func(self):
        return self.request.user.has_perm(self.object.asso.abreviation + '_update_projetphoning')

    def get_form(self):
        return ProjetPhoning_form(**self.get_form_kwargs())

    def form_valid(self, form):
        self.object = form.save()
        return redirect("adherents:phoning_projet_omplet")

    def get_success_url(self):
        return self.object.get_absolute_url()

class ProjetPhoning_supprimer(DeleteView, UserPassesTestMixin):
    model = ProjetPhoning
    template_name_suffix = '_supprimer'

    def test_func(self):
        return self.request.user.has_perm(self.object.asso.abreviation + '_delete_projetphoning')

    def get_success_url(self):
        return reverse('adherents:phoning_projet_courant')



class ProjetPhoning_liste(ListView,UserPassesTestMixin):
    model = ProjetPhoning
    context_object_name = "projets"
    template_name = "adherents/projetphoning_list.html"

    def test_func(self):
        return self.request.user.has_perm(self.object.asso.abreviation + '_liste_projetphoning')

    def get_queryset(self):
        params = dict(self.request.GET.items())
        if 'asso' in params:
            self.request.session["asso_abreviation"] = params['asso']
            self.qs = ProjetPhoning.objects.filter(asso__abreviation=params['asso'])
        else:
            self.qs = ProjetPhoning.objects.filter(asso__abreviation__in=self.request.user.getListeAbreviationsAssos())
        return self.qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['asso_list'] = [(x.abreviation, x.nom,) for x in Asso.objects.all().order_by("id") if
                                self.request.user.est_autorise(x.abreviation)]

        #context["filter"] = filter
        return context
