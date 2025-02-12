from django import forms
from .models import Adhesion, Adherent, InscriptionMail, ListeDiffusion, Comm_adherent, Contact, ContactContact
from .constantes import list_ape
from local_summernote.widgets import SummernoteWidget
from .models import ProjetPhoning


class AdhesionForm(forms.ModelForm):

    class Meta:
        model = Adhesion
        fields = ['date_cotisation', 'montant', 'moyen', 'detail']
        widgets = {
            'date_cotisation': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),

        }


class AdhesionForm_adherent(forms.ModelForm):

    class Meta:
        model = Adhesion
        fields = ['adherent', 'date_cotisation', 'montant', 'moyen', 'detail']
        widgets = {
            'date_cotisation': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),

        }


class AdherentForm(forms.ModelForm):
    rue = forms.CharField(label="Rue", required=False)
    code_postal = forms.CharField(label="Code postal*", initial="66000", required=False)
    commune = forms.CharField(label="Commune", initial="Perpignan", required=False)
    telephone = forms.CharField(label="Téléphone", required=False)
    production_ape = forms.ChoiceField(label="Production",
                                       help_text="Selectionner la production correspondant à votre code APE dans la liste",
                                       choices=list_ape)

    class Meta:
        model = Adherent
        fields = ['nom', 'prenom', 'statut', 'nom_gaec', 'email', 'production_ape','rue', 'code_postal', 'commune', 'telephone', ]


        widgets = {
            'date_cotisation': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            }

class AdherentChangeForm(forms.ModelForm):
    production_ape = forms.ChoiceField(label="Production", help_text="Selectionner la production correspondant à votre code APE dans la liste", choices=list_ape)

    class Meta:
        model = Adherent
        fields = ['nom', 'prenom', 'statut', 'nom_gaec', 'email', 'production_ape', ]

        widgets = {
            'date_cotisation': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            }



class InscriptionMailForm(forms.ModelForm):
    adherent = forms.ModelChoiceField(queryset=Adherent.objects.all().order_by('nom'), required=True, label="Adhérent", )

    class Meta:
        model = InscriptionMail
        fields = [ "adherent", 'commentaire',]

class InscriptionMailAdherentALsteForm(forms.ModelForm):

    class Meta:
        model = InscriptionMail
        fields = [ 'liste_diffusion', 'commentaire']
        widgets = {
            'commentaire': SummernoteWidget(),
        }

class InscriptionMail_listeAdherent_Form(forms.ModelForm):

    class Meta:
        model = InscriptionMail
        fields = [ 'liste_diffusion', 'adherent', 'commentaire',]
        widgets = {
            'commentaire': SummernoteWidget(),
        }


class ListeDiffusionForm(forms.ModelForm):
    class Meta:
        model = ListeDiffusion
        fields = ['nom']


class Comm_adh_form(forms.ModelForm):
    class Meta:
        model = Comm_adherent
        fields = ['commentaire']



class Contact_form(forms.ModelForm):
    telephone = forms.CharField(label="Téléphone", required=False)
    code_postal = forms.CharField(label="Code postal*", required=False)
    commune = forms.CharField(label="Commune",  required=False)
    rue = forms.CharField(label="Rue", required=False)
    adherent =  forms.ModelChoiceField(queryset=Adherent.objects.order_by('nom'), required=False,
                              label="Adhérent lié ?", )
    class Meta:
        model = Contact
        fields = ['nom', 'prenom', 'telephone', 'email', 'rue', 'commune', 'code_postal', 'commentaire', 'adherent']


class Contact_update_form(forms.ModelForm):
    telephone = forms.CharField(label="Téléphone", required=False)
    code_postal = forms.CharField(label="Code postal", required=False)
    commune = forms.CharField(label="Commune", required=False)
    rue = forms.CharField(label="Rue", required=False)

    class Meta:
        model = Contact
        fields = ['nom', 'prenom', 'telephone', 'email', 'rue', 'commune', 'code_postal', 'commentaire']


class ContactContact_form(forms.ModelForm):
    class Meta:
        model = ContactContact
        fields = [ 'statut', 'commentaire',]


class ListeTel_form(forms.Form):
    telephones = forms.CharField(label="Liste de Téléphones, séparés par une virgule", required=True,
        widget=forms.Textarea,
    )

class csvFile_form(forms.Form):
    fichier_csv = forms.FileField(label="Selectionner CSV avec colonnes nom,prenom,telephone (+ en option: email, rue, commune, code_postal)", required=True, )


class csvText_form(forms.Form):
    texte_csv = forms.CharField(label=" copier/coller le contenu du csv ici", required=True,
        widget=forms.Textarea,
    )



class ProjetPhoning_form(forms.ModelForm):
    class Meta:
        model = ProjetPhoning
        fields = [ "titre", 'asso', 'description']
        widgets = {
            'description': SummernoteWidget(),
        }
