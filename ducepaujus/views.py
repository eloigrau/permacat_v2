from django.shortcuts import render
from .forms import ContactForm


# Create your views here.
def accueil(request):
    form_contact = ContactForm(request.POST or None)
    msg = None
    msg2 = None
    anchor = None

    if request.method == 'POST':
        anchor = "contact"
        if form_contact.is_valid():
            form_contact.save()
            msg2 = "Votre message a bien été envoyé, merci !"
        elif form_contact.errors:
            msg2 = "Une erreur s'est produite lors de l'envoi du message, veuillez réessayer"

    return render(request, 'ducepaujus/index.html', {"msg":msg, "msg2":msg2, "form": form_contact, "anchor":anchor })
