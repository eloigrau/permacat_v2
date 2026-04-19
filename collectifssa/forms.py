from django import forms
from django.core.mail import send_mail
from bourseLibre.settings.production import SERVER_EMAIL, LOCALL
from .models import Message_collectifssa, InscriptionCLA
from local_summernote.widgets import SummernoteWidget
from .envoi_mail import envoyerMailPermAgora

LIST_EMAIL_SUIVI = ["CollectifSSA.Elne@proton.me ", ]

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


class InscriptionForm(forms.ModelForm):

    class Meta:
        model = InscriptionCLA
        fields = ['nom', "email", "msg"]
        widgets = {
             'msg': SummernoteWidget(),
        }

    def save(self,):
        instance = super(InscriptionForm, self).save()
        if not LOCALL:
            sujet = '[Collectifssa] Nouvelle inscription'
            message_html = "Inscirption au CLA de : " + self.cleaned_data['email']
            send_mail(sujet, message_html,  SERVER_EMAIL, LIST_EMAIL_SUIVI, fail_silently=False, html_message=message_html)


        return instance