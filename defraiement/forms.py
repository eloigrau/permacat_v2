from django import forms
from django.utils.text import slugify
import itertools
from local_summernote.widgets import SummernoteWidget
from bourseLibre.models import Asso
from photologue.models import Album
from .models import Choix, ParticipantReunion, Reunion, Distance_ParticipantReunion, NoteDeFrais
from django.core.exceptions import ValidationError
from bourseLibre.utils import slugify_pcat
from adherents.models import Adherent

class DateInput(forms.DateInput):
    input_type = 'date'

class ReunionForm(forms.ModelForm):

    class Meta:
        model = Reunion
        fields = ['categorie', 'titre', 'description', 'start_time']
        widgets = {
            'contenu': SummernoteWidget(),
              'start_time':  forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }

    def __init__(self, asso_slug, *args, **kwargs):
        super(ReunionForm, self).__init__(*args, **kwargs)
        self.fields['categorie'].choices = [x for x in Choix.type_reunion if x[1] in Choix.type_reunion_asso[asso_slug]]

    def save(self, userProfile):
        instance = super(ReunionForm, self).save(commit=False)

        max_length = Reunion._meta.get_field('slug').max_length
        instance.slug = orig = slugify_pcat(instance.titre, max_length)

        for x in itertools.count(1):
            if not Reunion.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        instance.auteur = userProfile

        instance.save()

        return instance


class ReunionChangeForm(forms.ModelForm):

    class Meta:
        model = Reunion
        fields = ['asso', 'categorie', 'titre', 'description', 'start_time', 'estArchive']
        widgets = {
            'contenu': SummernoteWidget(),
            'start_time': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
        }

class ParticipantReunionMultipleChoiceForm(forms.Form):
    participants = forms.ModelMultipleChoiceField(queryset=ParticipantReunion.objects.all(), required=True,
                                  label="",
        widget=forms.CheckboxSelectMultiple,)

    def __init__(self, asso_slug, *args, **kwargs):
        super(ParticipantReunionMultipleChoiceForm, self).__init__(*args, **kwargs)
        self.fields['participants'].choices = [(x.id, x.nom) for x in ParticipantReunion.objects.filter(asso__slug=asso_slug).order_by('nom')]

class ParticipantReunionChoiceForm(forms.Form):
    participant = forms.ModelChoiceField(queryset=ParticipantReunion.objects.all().order_by('nom'), required=True,
                                  label="Participant ", )

    def __init__(self, asso_slug, *args, **kwargs):
        super(ParticipantReunionChoiceForm, self).__init__(*args, **kwargs)
        self.fields['participant'].choices = [(x.id, x.nom) for x in ParticipantReunion.objects.filter(asso__slug=asso_slug).order_by('nom')]

class PrixMaxForm(forms.Form):
    prixMax = forms.CharField(required=True, label="Defraiement maximum (euros)",initial="2000" )
    tarifKilometrique = forms.CharField(required=True, label="Tarif kilometrique maximum", initial="0.6")


class ParticipantReunionForm(forms.ModelForm):
    class Meta:
        model = ParticipantReunion
        fields = ['nom']

    def save(self, adresse, asso):
        instance = super(ParticipantReunionForm, self).save(commit=False)
        instance.adresse = adresse
        instance.asso = asso
        instance.save()
        return instance

    def __init__(self, request, nom=None, *args, **kwargs):
        super(ParticipantReunionForm, self).__init__(request, *args, **kwargs)
        if nom:
            self.fields["nom"].initial = nom

class AdresseReunionForm(forms.ModelForm):
    class Meta:
        model = Reunion
        fields = ['adresse', ]

    def save(self, reunion, adresse):
        instance = super(ParticipantReunionForm, self).save(commit=False)
        instance.adresse = adresse
        instance.save()
        return instance


class Distance_ParticipantReunionForm(forms.ModelForm):

    class Meta:
        model = Distance_ParticipantReunion
        fields = ['type_trajet', 'distance', 'contexte_distance',]


class ChoixAdherentConf(forms.Form):
    adherent = forms.ModelChoiceField(queryset=Adherent.objects.all().order_by('nom'), required=True, label="Adhérent", )

    class Meta:
        fields = ['adherent']

class NoteDeFrais_form(forms.ModelForm):
    participant = forms.ModelChoiceField(queryset=ParticipantReunion.objects.all().order_by('nom'), required=False,
                                  label="Participant ", )

    def __init__(self, asso_slug, *args, **kwargs):
        super(NoteDeFrais_form, self).__init__(*args, **kwargs)
        self.fields['participant'].choices = [("", "---------"), ] + [(x.id, x.nom) for x in ParticipantReunion.objects.filter(asso__slug=asso_slug).order_by('nom')]

    class Meta:
        model = NoteDeFrais
        fields = ['titre', 'participant', 'date_note', 'montant', 'categorie', 'moyen', 'detail' ]


        widgets = {
              'date_note':  forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            'detail': SummernoteWidget(),
        }

class NoteDeFrais_update_form(forms.ModelForm):
    participant = forms.ModelChoiceField(queryset=ParticipantReunion.objects.all().order_by('nom'), required=True,
                                  label="Payé par", )

    def __init__(self, asso_slug, *args, **kwargs):
        super(NoteDeFrais_update_form, self).__init__(*args, **kwargs)
        self.fields['participant'].choices = [("", "---------"), ] + [(x.id, x.nom) for x in ParticipantReunion.objects.filter(asso__slug=asso_slug).order_by('nom')]

    class Meta:
        model = NoteDeFrais
        fields = ['titre', 'participant', 'date_note', 'montant', 'categorie', 'moyen', 'detail', 'estArchive' ]

        widgets = {
              'date_note':  forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),

            'detail': SummernoteWidget(),
        }