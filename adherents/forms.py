from django import forms
from .models import Adhesion, Adherent


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
class AdherentForm(forms.ModelForm):
    rue = forms.CharField(label="Rue (à peu près, champs invisible par les autres membres mais pour un affichage sur la carte)", required=False)
    code_postal = forms.CharField(label="Code postal*", initial="66000", required=False)
    commune = forms.CharField(label="Commune", initial="Perpignan", required=False)
    telephone = forms.CharField(label="Téléphone", required=False)
    latitude = forms.FloatField(label="Latitude", initial="42", required=False,)
    longitude = forms.FloatField(label="Longitude", initial="2", required=False,)

    class Meta:
        model = Adherent
        fields = ['nom', 'prenom', 'statut', 'email', 'rue', 'code_postal', 'commune', 'telephone', 'latitude', 'longitude', ]

        widgets = {
            'date_cotisation': forms.DateInput(
                format=('%Y-%m-%d'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            }
