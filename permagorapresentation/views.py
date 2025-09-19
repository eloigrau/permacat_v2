from django.shortcuts import render
from .forms import ContactForm
from bourseLibre.forms import CaptchaForm


# Create your views here.
def accueil(request):
    form_captcha = None
    msg = None
    msg2 = None
    anchor = None
    if request.user.is_anonymous:
        form_captcha = CaptchaForm(request.POST or None, )
        form_contact = ContactForm(request.POST or None)
    else:
        form_contact = ContactForm(request.POST or None, initial={"nom":request.user.username, "email":request.user.email, })


    if request.method == 'POST':
        anchor = "contact"
        if form_contact.is_valid() and (not request.user.is_anonymous or form_captcha.is_valid()):
            form_contact.save()
            msg2 = "<em>Votre message a bien été envoyé, merci !</em>"
        elif form_contact.errors:
            msg2 = "<em>Une erreur s'est produite lors de l'envoi du message (%s), veuillez réessayer ou envoyer un mail à permagora66@gmail.com </em>"%form_contact.errors

    return render(request, 'permagorapresentation/index.html', {"msg":msg, "msg2":msg2, "form": form_contact,"form_captcha": form_captcha, "anchor":anchor })
