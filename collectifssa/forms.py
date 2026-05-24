from django import forms
from django.core.mail import send_mail
from bourseLibre.settings.production import SERVER_EMAIL, LOCALL
from .models import Message_collectifssa, InscriptionCLA, Covoit
from local_summernote.widgets import SummernoteWidget
from .envoi_mail import envoyerMailPermAgora

LIST_EMAIL_SUIVI = ["CollectifSSA.Elne@proton.me ", "eloi.grau@gmail.com"]

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


class CommMessage_form(forms.ModelForm):

    class Meta:
        model = Message_collectifssa
        fields = ["commentaire"]
        widgets = {
             'commentaire': SummernoteWidget(),
        }
class CommCLA_form(forms.ModelForm):

    class Meta:
        model = InscriptionCLA
        fields = ["commentaire"]
        widgets = {
             'commentaire': SummernoteWidget(),
        }

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
            message_html = "Inscription au CLA de : " + self.cleaned_data['nom'] + " , "+self.cleaned_data['email'] +" " + self.cleaned_data['msg']
            send_mail(sujet, message_html,  SERVER_EMAIL, LIST_EMAIL_SUIVI, fail_silently=False, html_message=message_html)


        return instance

class CovoitForm(forms.ModelForm):

    class Meta:
        model = Covoit
        fields = ['nom', 'villeDepart', "telephone", "besoin"]
        widgets = {
            'msg': SummernoteWidget(),
        }

    def __init__(self, inscript, *args, **kwargs):
        super(CovoitForm, self).__init__(*args, **kwargs)
        if inscript:
            self.fields["nom"].initial = inscript.nom

    def save(self, ):
        instance = super(CovoitForm, self).save()
        if not LOCALL:
            sujet = '[Collectifssa] Inscription Coivoiturage CLA'
            message_html = "Inscription au covoiturage CLA : " + self.cleaned_data['nom'] + " , "+ self.cleaned_data['villeDepart'] \
                           +" , "+ self.cleaned_data['telephone']
            send_mail(sujet, message_html, SERVER_EMAIL, LIST_EMAIL_SUIVI, fail_silently=False,
                      html_message=message_html)

        return instance