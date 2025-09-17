from django.shortcuts import render
from .forms import ContactForm
from bourseLibre.forms import ContactMailForm, CaptchaForm


# Create your views here.
def accueil(request):
    form_captcha = None
    msg = None
    msg2 = None
    anchor = None
    form_contact = ContactForm(request.POST or None)
    if request.user.is_anonymous:
        form_captcha = CaptchaForm(request.POST or None, )

    if request.method == 'POST':
        anchor = "contact"
        if form_contact.is_valid() and (not request.user.is_anonymous or form_captcha.is_valid()):
            form_contact.save()
            msg2 = "Votre message a bien été envoyé, merci !"
        elif form_contact.errors:
            msg2 = "Une erreur s'est produite lors de l'envoi du message, veuillez réessayer"

    return render(request, 'permagorapresentation/index.html', {"msg":msg, "msg2":msg2, "form": form_contact,"form_captcha": form_captcha, "anchor":anchor })
