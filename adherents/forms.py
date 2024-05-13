from django import forms
from .models import Adhesion, Adherent, InscriptionMail, ListeDiffusionConf
from .constantes import list_ape
from local_summernote.widgets import SummernoteWidget


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
    rue = forms.CharField(label="Rue", required=False)
    code_postal = forms.CharField(label="Code postal*", initial="66000", required=False)
    commune = forms.CharField(label="Commune", initial="Perpignan", required=False)
    telephone = forms.CharField(label="Téléphone", required=False)
    production_ape = forms.ChoiceField(label="Production", help_text="Selectionner la production correspondant à votre code APE dans la liste", choices=list_ape)

    class Meta:
        model = Adherent
        fields = ['nom', 'prenom', 'statut', 'nom_gaec', 'email', 'production_ape', 'rue', 'code_postal', 'commune', 'telephone', ]

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


class ListeDiffusionConfForm(forms.ModelForm):
    class Meta:
        model = ListeDiffusionConf
        fields = ['nom']

