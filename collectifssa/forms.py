from django import forms
from django.core.mail import send_mail
from bourseLibre.settings.production import SERVER_EMAIL, LOCALL
from .models import Message_collectifssa
from local_summernote.widgets import SummernoteWidget
from .envoi_mail import envoyerMailPermAgora

LIST_EMAIL_SUIVI = ['eloi.grau@gmail.com', "permagora66@gmail.com", ]

class ContactForm(forms.ModelForm):

    class Meta:
        model = Message_collectifssa
        fields = ['nom', "email", "msg"]
        widgets = {
             'msg': SummernoteWidget(),
        }

    def save(self,):
        instance = super(ContactForm, self).save()
        if not LOCALL:
            envoyeur = self.cleaned_data["nom"] + ' (' + self.cleaned_data["email"] + ')'
            sujet = '[Collectifssa] Nouveau message'
            message_html = envoyeur + " a envoyé le message: " + self.cleaned_data['msg']
            send_mail(sujet, message_html,  SERVER_EMAIL, LIST_EMAIL_SUIVI, fail_silently=False, html_message=message_html)

        return instance