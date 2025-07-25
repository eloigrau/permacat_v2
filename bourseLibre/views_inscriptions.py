# -*- coding: utf-8 -*-
'''
Created on 25 mai 2017

@author: tchenrezi
'''
from django.shortcuts import render, redirect
from django.core.exceptions import PermissionDenied
from .forms import ContactForm, InscriptionNewsletterForm, DesInscriptionNewsletterForm
from .models import Profil, Choix, Asso, Suivis, InscriptionNewsletter, Salon
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.core.mail import mail_admins, send_mass_mail
from django.views.decorators.csrf import csrf_exempt
from django.db.models import CharField
from django.db.models.functions import Lower
from actstream import actions, action
from actstream.models import Follow, following
from bourseLibre.settings.production import SERVER_EMAIL
from bourseLibre.settings import LOCALL
from .views import testIsMembreAsso, testIsMembreSalon
from .utils import reabonnerProfil_base, desabonnerProfil_base, desabonnerProfil_particuliers, reabonnerProfil_salons, desabonnerProfil_salons
CharField.register_lookup(Lower, "lower")

@login_required
@csrf_exempt
def suivre_conversations(request, actor_only=True):
    """
    """
    suivi, created = Suivis.objects.get_or_create(nom_suivi = 'conversations')

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi, send_action=False)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only, send_action=False)
    return redirect('conversations')

@login_required
@csrf_exempt
def suivre_produits(request, actor_only=True):
    suivi, created = Suivis.objects.get_or_create(nom_suivi = 'produits')

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi, send_action=False)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only, send_action=False)
    return redirect('marche')


@login_required
def sereabonner(request,):
    reabonnerProfil_base(request.user)
    return redirect('mesSuivis')
#
# @login_required
# def sedesabonner(request,):
#     for suiv in Choix.suivisPossibles:
#         suivi, created = Suivis.objects.get_or_create(nom_suivi=suiv)
#
#         if suivi in following(request.user):
#             actions.unfollow(request.user, suivi, send_action=False)
#
#     for slug in Choix.slugsAsso + ['public']:
#         if request.user.est_autorise(slug):
#             suivi, created = Suivis.objects.get_or_create(nom_suivi="articles_" + slug)
#             actions.unfollow(request.user, suivi, send_action=False)
#             suivi, created = Suivis.objects.get_or_create(nom_suivi="agora_" + slug)
#             actions.unfollow(request.user, suivi, send_action=False)
#
#     for salon in request.user.get_salons():
#         actions.unfollow(request.user, salon.getSuivi(), send_action=False)
#
#     return redirect('mesSuivis')

@login_required
def sedesabonner(request,):
    desabonnerProfil_base(request.user)
    return redirect('mesSuivis')

@login_required
def sedesabonner_salons(request,):
    desabonnerProfil_salons(request.user)
    return redirect('mesSuivis')

@login_required
def sereabonner_salons(request,):
    reabonnerProfil_salons(request.user)
    return redirect('mesSuivis')

@login_required
def sedesabonner_particuliers(request,):
    params = dict(request.GET.items())
    if "user" in params and request.user.is_superuser:
        desabonnerProfil_particuliers(Profil.objects.get(username=params["user"]))
    else:
        desabonnerProfil_particuliers(request.user)
    return redirect('mesSuivis')


@login_required
def supprimerTousMesAbonnement(request):
    desabonnerProfil_particuliers(request.user)
    desabonnerProfil_salons(request.user)
    desabonnerProfil_base(request.user)
    return redirect('mesSuivis')

@login_required
def reinitialiserTousMesAbonnement(request):
    reabonnerProfil_salons(request.user)
    reabonnerProfil_base(request.user)
    return redirect('mesSuivis')

def inscription_newsletter(request):
    form = InscriptionNewsletterForm(request.POST or None)
    if form.is_valid():
        inscription = form.save(commit=False)
        inscription.save()
        return render(request, 'merci.html', {'msg' :"Vous êtes inscrits à la newsletter"})
    return render(request, 'registration/inscription_newsletter.html', {'form':form})

def desinscription_newsletter(request):
    form = DesInscriptionNewsletterForm(request.POST or None)
    msg = ""
    if form.is_valid():
        try:

            inscription = InscriptionNewsletter.objects.get(email=form.cleaned_data["email"])
            inscription.delete()
            msg = "Inscription à la newsletter de "+ form.cleaned_data['email'] +" supprimée"
            if request.user.is_authenticated:
                if request.user.email == form.cleaned_data["email"]:
                    p = Profil.objects.get(email=form.cleaned_data["email"])
                    p.inscrit_newsletter = False
                    p.save()
                    msg += "Inscription à la newsletter de "+ form.cleaned_data['email'] +" supprimée du profil"

        except Exception as e:
            msg = "Une erreur est survenue : " + str(e)

        action.send(request.user, verb="desinscription", description=form.cleaned_data["email"] + " : " + msg)
        return render(request, 'merci.html', {'msg' :msg})
    return render(request, 'registration/desinscription_newsletter.html', {'form':form, 'msg':msg})


@login_required
def inscription_permagora(request):
    asso=Asso.objects.get(slug='scic')
    if request.user.adherent_scic:
        request.user.adherent_scic = False
        request.user.save()
        suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_scic')
        actions.unfollow(request.user, suivi, send_action=False)
        action.send(request.user, verb='inscription_permagora', target=asso, url=request.user.get_absolute_url(),
                    description="s'est retiré.e du groupe PermAgora")
    else:
        request.user.adherent_scic = True
        request.user.save()
        suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_scic')
        actions.follow(request.user, suivi, send_action=False)
        action.send(request.user, verb='inscription_permagora', target=asso, url=request.user.get_absolute_url(),
                    description="s'est inscrit.e au groupe PermAgora")
    return redirect('presentation_asso', asso='scic')


@login_required
def inscription_citealt(request):
    asso=Asso.objects.get(slug='citealt')
    if request.user.adherent_citealt:
        request.user.adherent_citealt = False
        request.user.save()
        suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_citealt')
        actions.unfollow(request.user, suivi, send_action=False)
        action.send(request.user, verb='inscription_citealt', target=asso, url=request.user.get_absolute_url(),
                    description="s'est retiré.e du groupe Cité Altruiste")
    else:
        request.user.adherent_citealt = True
        request.user.save()
        suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_citealt')
        actions.follow(request.user, suivi, send_action=False)
        action.send(request.user, verb='inscription_citealt', target=asso, url=request.user.get_absolute_url(),
                    description="s'est inscrit.e dans le groupe Cité Altruiste")
    return redirect('presentation_asso', asso='citealt')

@login_required
def inscription_viure(request):
    asso=Asso.objects.get(slug='viure')
    if request.user.adherent_viure:
        request.user.adherent_viure = False
        request.user.save()
        suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_viure')
        actions.unfollow(request.user, suivi, send_action=False)
        url = reverse('presentation_asso', kwargs={'asso': 'viure'})
        action.send(request.user, verb='inscription_viure', target=asso, url=request.user.get_absolute_url(),
                    description="s'est retiré.e du groupe Viure")
    else:
        request.user.adherent_viure = True
        request.user.save()
        suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_viure')
        actions.follow(request.user, suivi, send_action=False)
        action.send(request.user, verb='inscription_viure', target=asso, url=request.user.get_absolute_url(),
                    description="s'est inscrit.e dans le groupe Viure")
    return redirect('presentation_asso', asso='viure')


@login_required
def inscription_asso(request, asso_slug):
    asso=Asso.objects.get(slug=asso_slug)
    if getattr(request.user, "adherent_"+asso_slug):
        setattr(request.user, "adherent_"+asso_slug, False)
        request.user.save()
        suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_'+asso_slug)
        actions.unfollow(request.user, suivi, send_action=False)
        url = reverse('presentation_asso', kwargs={'asso': asso_slug})
        action.send(request.user, verb='inscription_'+asso_slug, target=asso, url=request.user.get_absolute_url(),
                    description="s'est retiré.e du groupe " + asso.nom)
    else:
        setattr(request.user, "adherent_"+asso_slug, True)
        request.user.save()
        suivi, created = Suivis.objects.get_or_create(nom_suivi='articles'+asso_slug)
        actions.follow(request.user, suivi, send_action=False)
        action.send(request.user, verb='inscription_'+asso_slug, target=asso, url=request.user.get_absolute_url(),
                    description="s'est inscrit.e dans le groupe " + asso.nom)
    return redirect('presentation_asso', asso=asso_slug)

@login_required
def inscription_bzz2022(request):
    asso = Asso.objects.get(slug='bzz2022')
    if request.user.adherent_bzz2022:
        request.user.adherent_bzz2022 = False
        request.user.save()
        suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_bzz2022')
        actions.unfollow(request.user, suivi, send_action=False)
        url = reverse('presentation_asso', kwargs={'asso': 'bzz2022'})
        action.send(request.user, verb='inscription_bzz2022', target=asso, url=request.user.get_absolute_url(),
                    description="s'est retiré.e du groupe Bzzz")
    else:
        request.user.adherent_bzz2022 = True
        request.user.save()
        suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_bzz2022')
        actions.follow(request.user, suivi, send_action=False)
        action.send(request.user, verb='inscription_bzz2022', target=asso, url=request.user.get_absolute_url(),
                    description="s'est inscrit.e dans le groupe Bzzz")
    return redirect('presentation_asso', asso='bzz2022')

@login_required
def inscription_jp(request):
    asso=Asso.objects.get(slug='jp')
    if request.user.adherent_jp:
        request.user.adherent_jp = False
        request.user.save()
        suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_jp')
        actions.unfollow(request.user, suivi, send_action=False)
        action.send(request.user, verb='inscription_jp', target=asso, url=request.user.get_absolute_url(),
                    description="s'est retiré.e du groupe des Jardins Partagés")
    else:
        request.user.adherent_jp = True
        request.user.save()
        suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_jp')
        actions.follow(request.user, suivi, send_action=False)
        action.send(request.user, verb='inscription_jp', target=asso, url=request.user.get_absolute_url(),
                    description="s'est inscrit.e dans le groupe des Jardins Partagés")
    return redirect('jardins:accueil')

@login_required
def contacter_newsletter(request):
    if not request.user.adherent_pc:
        return render(request, "notPermacat.html")

    if request.method == 'POST':
        form = ContactForm(request.POST or None, )
        if form.is_valid():
            sujet = "[permacat] Newsletter - " +  form.cleaned_data['sujet']
            message = form.cleaned_data['msg']
            emails = [profil.email for profil in Profil.objects.filter(inscrit_newsletter=True)] + [profil.email for
                                                                                                    profil in
                                                                                                    InscriptionNewsletter.objects.all()]
            if emails and not LOCALL:
                try:
                    send_mass_mail([(sujet, message, SERVER_EMAIL, emails), ])
                except:
                    sujet = "[permacat admin] Erreur lors de l'envoi du mail"
                    message_txt = message + '\n'.join(emails)

                    try:
                        mail_admins(sujet, message_txt)
                    except:
                        print("erreur de la fonction contacterNewsletter (views.py)")
                        pass
            return render(request, 'contact/message_envoye.html', {'sujet': form.cleaned_data['sujet'], 'msg': message,
                                                           'envoyeur': request.user.username + " (" + request.user.email + ")",
                                                           "destinataires": emails})
    else:
        form = ContactForm()
    return render(request, 'contact/contact_newsletter.html', {'form': form, })



@login_required
def contacter_adherents(request):
    if not request.user.adherent_pc:
        return render(request, "notPermacat.html")

    if request.method == 'POST':
        form = ContactForm(request.POST or None, )
        if form.is_valid():
            sujet = "[permacat] Newsletter - " +  form.cleaned_data['sujet']
            message = form.cleaned_data['msg']
            emails = [profil.email for profil in Profil.objects.filter(adherent_pc=True)]

            if emails and not LOCALL:
                try:
                    send_mass_mail([(sujet, message, SERVER_EMAIL, emails), ])
                except:
                    sujet = "[permacat admin] Erreur lors de l'envoi du mail"
                    message_txt = message + '\n'.join(emails)

                    try:
                        mail_admins(sujet, message_txt)
                    except:
                        print("erreur de la fonction contacterAdherents (views.py)")
                        pass
            return render(request, 'contact/message_envoye.html', {'sujet': form.cleaned_data['sujet'], 'msg': message,
                                                           'envoyeur': request.user.username + " (" + request.user.email + ")",
                                                           "destinataires": emails})
    else:
        form = ContactForm()
    return render(request, 'contact/contact_adherents.html', {'form': form, })



@login_required
@csrf_exempt
def suivre_agora(request, asso, actor_only=True):
    asso = testIsMembreAsso(request, asso)
    if not isinstance(asso, Asso):
        raise PermissionDenied

    suivi, created = Suivis.objects.get_or_create(nom_suivi='agora_' + str(asso.slug))

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only)
    return redirect('agora', asso=asso.slug)

@login_required
@csrf_exempt
def suivre_salon(request, slug_salon, actor_only=True):
    if slug_salon != "accueil":
        salon = testIsMembreSalon(request, slug_salon)
        if not isinstance(salon, Salon):
            raise PermissionDenied
    suivi, created = Suivis.objects.get_or_create(nom_suivi='salon_' + str(slug_salon))

    if suivi in following(request.user):
        actions.unfollow(request.user, suivi)
    else:
        actions.follow(request.user, suivi, actor_only=actor_only)

    if slug_salon == "accueil":
        return redirect("salon_accueil")
    return redirect('salon', slug=salon.slug)
