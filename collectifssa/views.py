from django.shortcuts import render
from .forms import ContactForm
from bourseLibre.forms import CaptchaForm
from bourseLibre.models import Profil
from actstream import action


# Create your views here.
def accueil(request):
    msg = None
    msg2 = None
    anchor = None
    if request.user.is_anonymous:
        form_captcha = CaptchaForm(request.POST or None, )
        form_contact = ContactForm(request.POST or None)
    else:
        form_captcha = None
        form_contact = ContactForm(request.POST or None, initial={"nom":request.user.username, "email":request.user.email, })

    if request.method == 'POST':
        anchor = "contact"
        if form_contact.is_valid() and (not request.user.is_anonymous or form_captcha.is_valid()):
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

    return render(request, 'collectifssa/index.html', {"msg":msg, "msg2":msg2, "form": form_contact, "form_captcha": form_captcha, "anchor":anchor })
#index #left-sidebar