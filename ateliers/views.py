# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.urls import reverse_lazy
from .models import CommentaireAtelier, Choix, Atelier, InscriptionAtelier
from .forms import AtelierForm, CommentaireAtelierForm, AtelierChangeForm, ContactParticipantsForm, CommentaireAtelierChangeForm
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, UpdateView, DeleteView
from django.views.decorators.csrf import csrf_exempt
from blog.models import Article
from actstream.models import following
from bourseLibre.settings.production import SERVER_EMAIL
from datetime import timedelta

from django.utils.timezone import now
from django.dispatch import Signal
from bourseLibre.models import Suivis, Profil
from bourseLibre.views_base import DeleteAccess
from bourseLibre.views_admin import send_mass_html_mail
from django.contrib import messages

from bourseLibre.constantes import Choix as Choix_global
from actstream import actions, action
from actstream.models import Action as Actstream_action
from django.db.models import Q

from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from bs4 import BeautifulSoup
from webpush import send_user_notification
from django.templatetags.static import static

def accueil(request):
    return redirect("ateliers:index_ateliers")
    #return render(request, 'ateliers/accueil.html')


@login_required
def ajouterAtelier(request, article_slug=None):
    form = AtelierForm(request, request.POST or None)
    if article_slug:
        article = Article.objects.get(slug=article_slug)
    else:
        article = None
    if form.is_valid():
        atelier = form.save(request, article)
        action.send(request.user, verb='atelier_nouveau', action_object=atelier, url=atelier.get_absolute_url(),
                     description="a ajouté l'atelier: '%s'" % atelier.titre)
        return redirect(atelier.get_absolute_url())
    return render(request, 'ateliers/atelier_ajouter.html', { "form": form, })


# @login_required
class ModifierAtelier(UpdateView):
    model = Atelier
    form_class = AtelierChangeForm
    template_name_suffix = '_modifier'

    def get_object(self):
        return Atelier.objects.get(slug=self.kwargs['slug'])

    def form_valid(self, form):
        self.object = form.save()
        self.object.date_modification = now()
        self.object.save()
        if self.object.date_modification - self.object.date_creation > timedelta(minutes=10):
            action.send(self.request.user, verb='atelier_modifier', action_object=self.object, url=self.object.get_absolute_url(),
                         description="a modifié l'atelier: '%s'" % self.object.titre)
        return HttpResponseRedirect(self.object.get_absolute_url())

    def save(self):
        return super(ModifierAtelier, self).save()

    def get_form(self, *args, **kwargs):
        form = super(ModifierAtelier, self).get_form(*args, **kwargs)
        form.fields["asso"].choices = [x for i, x in enumerate(form.fields["asso"].choices) if
                                        self.request.user.estMembre_str(x[1])]
        return form

class SupprimerAtelier(DeleteAccess, DeleteView):
    model = Atelier
    success_url = reverse_lazy('ateliers:index_ateliers')
    template_name_suffix = '_supprimer'

    def get_object(self):
        return Atelier.objects.get(slug=self.kwargs['slug'])

@login_required
def inscriptionAtelier(request, slug):
    atelier = get_object_or_404(Atelier, slug=slug)
    if not InscriptionAtelier.objects.filter(user=request.user, atelier=atelier):
        inscript = InscriptionAtelier(user=request.user, atelier=atelier)
        inscript.save()
        action.send(request.user, verb='atelier_inscription', action_object=atelier, url=atelier.get_absolute_url(),
                     description="s'est inscrit-e à l'atelier: '%s'" % atelier.titre)
        #act = Actstream_action.objects.model_actions(atelier, actor_content_type=3, actor_object_id=request.user.id)
        #for a in act:
        #    a.delete()

    messages.info(request, 'Vous êtes bien inscrit.e à cet atelier, notez le dans votre agenda !')
    return redirect(atelier.get_absolute_url())

@login_required
def annulerInscription(request, slug):
    atelier = get_object_or_404(Atelier, slug=slug)
    inscript = InscriptionAtelier.objects.filter(user=request.user, atelier=atelier)
    inscript.delete()
    action.send(request.user, verb='atelier_désinscription', action_object=atelier, url=atelier.get_absolute_url(),
                 description="s'est désinscrit de l'atelier: '%s'" % atelier.titre)
    return redirect(atelier.get_absolute_url())

@login_required
def contacterParticipantsAtelier(request, slug):
    atelier = get_object_or_404(Atelier, slug=slug)
    form = ContactParticipantsForm(request.POST or None, )
    inscrits = [x[0] for x in InscriptionAtelier.objects.filter(atelier=atelier).values_list('user__email')]
    try:
        referent = Profil.objects.get(username=atelier.referent)
        inscrits.append(referent.email)
    except:
        pass
    if form.is_valid():
        sujet = "[Permacat] Au sujet de l'atelier Permacat '" + atelier.titre +"' "
        message_html = str(request.user.username) + " ("+ str(request.user.email)+") a écrit le message suivant aux participants : \n"
        message_html += form.cleaned_data['msg']
        message_html += "\n (ne pas répondre à ce message, utiliser <a href='https://www.perma.cat"+ atelier.get_absolute_url() +" '>l'atelier sur le site perma.cat</a> :)"
        messagetxt = BeautifulSoup(message_html).get_text()
        send_mass_html_mail([(sujet, messagetxt, message_html, SERVER_EMAIL, inscrits) ], fail_silently=False)

    return render(request, 'ateliers/contacterParticipantsAtelier.html', {'atelier': atelier,  'form': form,  'inscrits':inscrits})


@login_required
def lireAtelier_slug(request, slug):
    atelier = get_object_or_404(Atelier, slug=slug)
    return lireAtelier(request, atelier)

@login_required
def lireAtelier_id(request, id):
    atelier = get_object_or_404(Atelier, id=id)
    return lireAtelier(request, atelier)

@login_required
def lireAtelier(request, atelier):
    commentaires = CommentaireAtelier.objects.filter(atelier=atelier).order_by("date_creation")
    inscrits = atelier.get_inscrits

    if not request.user.is_anonymous:
        user_inscrit = request.user.username in inscrits
    else:
        user_inscrit = []


    hit_count = HitCount.objects.get_for_object(atelier)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)

    form_comment = CommentaireAtelierForm(request.POST or None)
    if form_comment.is_valid():
        comment = form_comment.save(commit=False)
        comment.atelier = atelier
        comment.auteur_comm = request.user
        atelier.save()
        comment.save()
        url = atelier.get_absolute_url() + "#comm_"+str(comment.id)
        action.send(request.user, verb='atelier_message', url=url,
                    description="a commenté l'atelier: '%s'" % atelier.titre)
        suiveurs = [Profil.objects.get(username=atelier.auteur), ] + [x.user for x in InscriptionAtelier.objects.filter(atelier=atelier)]
        emails = [suiv.email for suiv in suiveurs]
        message = "L'atelier <a href='https://www.perma.cat" + url + "'>%s</a> a été commenté" %atelier.titre
        message_notif = "L'atelier %s a été commenté par %s" % (atelier.titre, request.user.username)
        action.send(request.user, verb='emails', url=url,
                    titre="a commenté l'atelier: '%s'" % atelier.titre,  message=message, emails=emails)

        payload = {"head": "atelier: '%s'" % atelier.titre, "body": message_notif,
                   "icon": static('android-chrome-256x256.png'), "url": atelier.get_absolute_url_site + "#comm_"+str(comment.id)}
        for suiv in suiveurs:
            try:
                send_user_notification(suiv, payload=payload, ttl=7200)
            except:
                pass

        return redirect(request.path)

    return render(request, 'ateliers/lireAtelier.html', {'atelier': atelier,  'form': form_comment, 'commentaires':commentaires, 'user_inscrit': user_inscrit, 'inscrits': inscrits},)


class ListeAteliers(ListView):
    model = Atelier
    context_object_name = "atelier_list"
    template_name = "ateliers/index_ateliers.html"
    paginate_by = 30

    def get_queryset(self):
        params = dict(self.request.GET.items())

        self.qs = Atelier.objects.filter(self.request.user.getQObjectsAssoAteliers() & Q(estArchive=False))

        if "categorie" in params:
            self.qs = self.qs.filter(categorie=params['categorie'])

        if "ordreTri" in params:
            self.qs = self.qs.order_by(params['ordreTri'])
        else:
            self.qs = self.qs.order_by('start_time', 'categorie')

        return self.qs.filter(start_time__gte=now(), start_time__isnull=False).order_by('start_time')

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context['list_propositions'] = self.qs.filter(start_time__isnull=True).order_by('start_time')
        context['list_passes'] = self.qs.filter(start_time__lt=now(), start_time__isnull=False).order_by('-start_time')

        cat= Atelier.objects.order_by('categorie').values_list('categorie', flat=True).distinct()
        context['categorie_list'] = [x for x in Choix.type_atelier if x[0] in cat]
        context['typeFiltre'] = "aucun"
        context['suivis'], created = Suivis.objects.get_or_create(nom_suivi="ateliers")

        context['ordreTriPossibles'] = ['-date_creation', 'categorie', 'titre' ]

        if 'categorie' in self.request.GET:
            context['typeFiltre'] = "categorie"
            context['categorie_courante'] = [x[1] for x in Choix.type_atelier if x[0] == self.request.GET['categorie']][0]
        if 'ordreTri' in self.request.GET:
            context['typeFiltre'] = "ordreTri"


        if "mc" in self.request.GET:
            context['typeFiltre'] = "mc"

        return context



class ModifierCommentaire(UpdateView):
    model = CommentaireAtelier
    form_class = CommentaireAtelierChangeForm
    template_name = 'modifierCommentaire.html'

    def get_object(self):
        return CommentaireAtelier.objects.get(id=self.kwargs['id'])

    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.object.commentaire and self.object.commentaire !='<br>':
            self.object.date_modification = now()
            self.object.save()
        else:
            self.object.delete()
        return redirect(self.object)



@login_required
@csrf_exempt
def suivre_ateliers(request, actor_only=True):
    suivi, created = Suivis.objects.get_or_create(nom_suivi='ateliers')

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only)
    return redirect('ateliers:index_ateliers')

#
# def copierAteliers(request):
#     for at in Atelier.objects.all():
#         if not Atelier_new.objects.filter(slug=at.slug).exists():
#             at_new = Atelier_new(categorie=at.categorie,
#                                statut=at.statut,
#                                titre=at.titre,
#                                slug=at.slug,
#                                description=at.description,
#                                materiel=at.materiel,
#                                referent=at.referent,
#                                auteur=at.auteur,
#                                start_time=at.start_time,
#                                heure_atelier=at.heure_atelier,
#                                heure_atelier_fin=at.heure_atelier_fin,
#                                date_creation=at.date_creation,
#                                date_modification=at.date_modification,
#                                tarif_par_personne=at.tarif_par_personne,
#                                asso=at.asso,
#                                article=at.article,
#                                estArchive=at.estArchive,
#                                nbMaxInscriptions=at.nbMaxInscriptions,
#                    )
#             at_new.save(sendMail=False)
#             for i in InscriptionAtelier.objects.filter(atelier=at):
#                 InscriptionAtelier_new.objects.create(user=i.user, atelier=at_new, date_inscription=i.date_inscription)
#
#             for c in CommentaireAtelier.objects.filter(atelier=at):
#                 CommentaireAtelier_new.objects.create(auteur_comm=c.auteur_comm, commentaire=c.commentaire,
#                                                       atelier=at_new,date_creation=c.date_creation)
#
#
#     return redirect('ateliers:index_ateliers')
#
#
#
# def copierAteliers_inverse(request):
#     for at in Atelier_new.objects.all():
#         if not Atelier.objects.filter(slug=at.slug).exists():
#             at_new = Atelier(categorie=at.categorie,
#                                statut=at.statut,
#                                titre=at.titre,
#                                slug=at.slug,
#                                description=at.description,
#                                materiel=at.materiel,
#                                referent=at.referent,
#                                auteur=at.auteur,
#                                start_time=at.start_time,
#                                heure_atelier=at.heure_atelier,
#                                heure_atelier_fin=at.heure_atelier_fin,
#                                date_creation=at.date_creation,
#                                date_modification=at.date_modification,
#                                tarif_par_personne=at.tarif_par_personne,
#                                asso=at.asso,
#                                article=at.article,
#                                estArchive=at.estArchive,
#                                nbMaxInscriptions=at.nbMaxInscriptions,
#                    )
#             at_new.save(sendMail=False)
#             for i in InscriptionAtelier_new.objects.filter(atelier=at):
#                 InscriptionAtelier.objects.create(user=i.user, atelier=at_new, date_inscription=i.date_inscription)
#
#             for c in CommentaireAtelier_new.objects.filter(atelier=at):
#                 CommentaireAtelier.objects.create(auteur_comm=c.auteur_comm, commentaire=c.commentaire,
#                                                       atelier=at_new,date_creation=c.date_creation)
#
#
#     return redirect('ateliers:index_ateliers')
#

@login_required
def get_qr_code(request, slug):
    qr_url = Atelier.objects.get(slug=slug).get_absolute_url_site
    return render(request, 'qr_code_template.html', {'qr_url': qr_url})



@login_required
def ateliersArchives(request):
    atelier_list = Atelier.objects.filter(request.user.getQObjectsAssoAteliers()).filter(estArchive=True)
    return render(request, 'ateliers/listAtelier_template.html', {'atelier_list': atelier_list})
