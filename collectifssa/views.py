from django.shortcuts import render
from .forms import ContactForm, InscriptionForm, CovoitForm, CommMessage_form
from .models import InscriptionCLA, Message_collectifssa, Covoit
from bourseLibre.forms import CaptchaForm
from bourseLibre.models import Profil
from actstream import action
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.views.generic import UpdateView


# Create your views here.
def accueil(request):
    msg = None
    msg2 = None
    msg3 = None
    anchor = None
    if request.user.is_anonymous:
        form_captcha = CaptchaForm(request.POST or None, )
        form_captcha2 = CaptchaForm(request.POST or None, )
        form_contact = ContactForm(request.POST or None)
        form_inscriptionCLA = InscriptionForm(request.POST or None)
    else:
        form_captcha = None
        form_captcha2 = None
        form_contact = ContactForm(request.POST or None, initial={"nom":request.user.username, "email":request.user.email, })
        form_inscriptionCLA = InscriptionForm(request.POST or None, initial={"nom":request.user.username, "email":request.user.email, })


    if request.method == 'POST':
        if form_contact.is_valid() and (not request.user.is_anonymous or form_captcha.is_valid()):
            anchor = "contact"
            try:
                if request.user.is_anonymous:
                    admin = Profil.objects.get(username="Eloi")
                    action.send(admin, verb='envoi_salon_prive',  url="/gestion/collectifssa/message_collectifssa/",
                        description="a envoyé un message au collectif SSA (anonyme)" )
                else:
                    action.send(request.user, verb='envoi_salon_prive',  url="/gestion/collectifssa/message_collectifssa/",
                        description="a envoyé un message au collectif SSA")
            except :
                pass
            form_contact.save()
            msg2 = "Votre message a bien été envoyé, merci !"
        elif form_contact.errors:
            msg2 = "<em>Une erreur s'est produite lors de l'envoi du message (%s), veuillez réessayer ou envoyer un mail à CollectifSSA.Elne@proton.me </em>"%form_contact.errors

        if form_inscriptionCLA.is_valid():
            try:
                if request.user.is_anonymous:
                    admin = Profil.objects.get(username="Eloi")
                    action.send(admin, verb='envoi_salon_prive',  url="/gestion/collectifssa/message_collectifssa/",
                        description="inscription Mail CLA (anonyme) " + form_inscriptionCLA.cleaned_data["email"] )
                else:
                    action.send(request.user, verb='envoi_salon_prive',  url="/gestion/collectifssa/message_collectifssa/",
                        description="inscription Mail CLA")
            except :
                pass
            form_inscriptionCLA.save()
            msg3 = "Votre inscription a bien été enregistrée, merci !"

    return render(request, 'collectifssa/index.html', {"msg":msg, "msg2":msg2, "msg3":msg3, "form": form_contact, "form_captcha": form_captcha, "form_inscriptionCLA": form_inscriptionCLA, "form_captcha2": form_captcha2, "anchor":anchor })
#index #left-sidebar


def inscriptionCLA(request):
    msg = None
    if request.user.is_anonymous:
        form_captcha = CaptchaForm(request.POST or None, )
        form_inscriptionCLA = InscriptionForm(request.POST or None)
    else:
        form_captcha = None
        form_inscriptionCLA = InscriptionForm(request.POST or None, initial={"nom":request.user.username, "email":request.user.email, })

        if InscriptionCLA.objects.filter(nom=request.user.username, email=request.user.email).exists():
            return render(request, 'collectifssa/inscriptionCLA.html', {"deja_inscrit":1,"msg":msg, "form_captcha": form_captcha, "form_inscriptionCLA": form_inscriptionCLA })

    if form_inscriptionCLA.is_valid():
        form_inscriptionCLA.save()
        try:
            admin = Profil.objects.get(username="Eloi")
            if request.user.is_anonymous:
                action.send(admin, verb='envoi_salon_prive',  url="/gestion/collectifssa/message_collectifssa/",
                    description="inscription Mail CLA (anonyme) " + form_inscriptionCLA.cleaned_data["email"] )
            else:
                action.send(admin, verb='envoi_salon_prive',  url="/gestion/collectifssa/message_collectifssa/",
                    description="inscription Mail CLA")
        except :
            pass
        msg = "Votre inscription a bien été enregistré-e, merci !"
        return render(request, 'collectifssa/inscriptionCLA.html', {"deja_inscrit":2, "msg":msg, "form_captcha": form_captcha, "form_inscriptionCLA": form_inscriptionCLA })


    return render(request, 'collectifssa/inscriptionCLA.html', {"deja_inscrit":0, "msg":msg, "form_captcha": form_captcha, "form_inscriptionCLA": form_inscriptionCLA })


def inscriptionCovoitCLA(request):
    msg = None
    inscript = None
    deja_inscrit = 0
    if request.user.is_anonymous:
        form_captcha = CaptchaForm(request.POST or None, )
        form_covoit = CovoitForm(inscript, request.POST or None)
    else:
        form_captcha = None
        form_covoit = CovoitForm(request.POST or None, initial={"nom":request.user.username })


    if form_covoit.is_valid():
        form_covoit.save()
        admin = Profil.objects.get(username="Eloi")
        action.send(admin, verb='envoi_salon_prive',  url="/gestion/collectifssa/message_collectifssa/",
            description="inscription Covoit CLA " + form_covoit.cleaned_data["nom"] )
        deja_inscrit = 1

        return render(request, 'collectifssa/covoitCLA.html', {"deja_inscrit":deja_inscrit, "msg":msg, "form_captcha": form_captcha, "form": form_covoit })


    return render(request, 'collectifssa/covoitCLA.html', {"deja_inscrit":deja_inscrit, "msg":msg, "form_captcha": form_captcha, "form": form_covoit })

@login_required
def voirMessages(request):
    if not request.user.adherent_ssa:
        return HttpResponseForbidden()

    listeMessages = Message_collectifssa.objects.filter().order_by('-date', "nom")
    listeInscriptions = InscriptionCLA.objects.filter().order_by('-date', "nom")
    listeCovoit = Covoit.objects.filter().order_by('-date', "nom")

    return render(request, 'collectifssa/voir_inscriptions.html', {"listeMessages":listeMessages, "listeInscriptions":listeInscriptions, "listeCovoit":listeCovoit})


class CommentaireMessage_modifier(UpdateView, ):
    model = Message_collectifssa
    form_class = CommMessage_form
    template_name = 'collectifssa/modifCommentaire.html'

    def get_initial(self):
        msg = Message_collectifssa.objects.get(pk=self.kwargs["pk"])
        return {
            'commentaire': msg.commentaire,
        }




