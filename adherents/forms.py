from django import forms
from .models import Adhesion, Adherent, InscriptionMail, ListeDiffusion, Comm_adherent, Contact, ContactContact
from .constantes import list_ape
from local_summernote.widgets import SummernoteWidget
from .models import ProjetPhoning
from bourseLibre.models import Asso

from django.core.exceptions import ValidationError

class AdhesionForm(forms.ModelForm):

    class Meta:
        model = Adhesion
        fields = ['date_cotisation', 'montant', 'moyen', 'detail']
        widgets = {
            'date_cotisation': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),

        }


class AdhesionForm_adherent(forms.ModelForm):

    class Meta:
        model = Adhesion
        fields = [ 'adherent', 'date_cotisation', 'montant', 'moyen', 'detail']
        widgets = {
            'date_cotisation': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),

        }

    def __init__(self, asso_slug, *args, **kwargs):
        super(AdhesionForm_adherent, self).__init__(*args, **kwargs)
        self.fields["adherent"].choices = [('', '(Choisir un adhérent)'), ] + [(x.id, x.nom + " " + x.prenom) for x in Adherent.objects.filter(asso__slug=asso_slug).order_by("nom", "prenom") ]



class AdherentForm_conf66(forms.ModelForm):
    rue = forms.CharField(label="Rue", required=False)
    code_postal = forms.CharField(label="Code postal*", initial="66000", required=False)
    commune = forms.CharField(label="Commune", initial="Perpignan", required=False)
    telephone = forms.CharField(label="Téléphone", required=False)
    production_ape = forms.ChoiceField(label="Production",
                                       help_text="Selectionner la production correspondant à votre code APE dans la liste",
                                       choices=list_ape)


    class Meta:
        model = Adherent
        fields = [ 'nom', 'prenom', 'statut', 'nom_gaec', 'email', 'production_ape','rue', 'code_postal', 'commune', 'telephone', ]


        widgets = {
            'date_cotisation': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            }

    def __init__(self, asso_slug, *args, **kwargs):
        super(AdherentForm_conf66, self).__init__(*args, **kwargs)
        self.asso_slug = asso_slug

    def clean(self):
        cleaned_data = self.cleaned_data

        try:
            Adherent.objects.get(nom__iexact=cleaned_data['nom'], prenom__iexact=cleaned_data['prenom'], asso__slug=self.asso_slug)
        except Adherent.DoesNotExist:
            pass
        else:
            raise ValidationError('Un adhérent avec ce nom et prénom existe déjà')

        # Always return cleaned_data
        return cleaned_data

class AdherentForm(forms.ModelForm):
    rue = forms.CharField(label="Rue", required=False)
    code_postal = forms.CharField(label="Code postal*", initial="66000", required=False)
    commune = forms.CharField(label="Commune", initial="Perpignan", required=False)
    telephone = forms.CharField(label="Téléphone", required=False)

    class Meta:
        model = Adherent
        fields = ['nom', 'prenom', 'email', 'rue', 'code_postal', 'commune', 'telephone', ]


        widgets = {
            'date_cotisation': forms.DateInput(
                format=('%d-%m-%Y'),
                attrs={'class': 'form-control',
                       'type': 'date'
                       }),
            }

    def __init__(self, asso_slug, *args, **kwargs):
        super(AdherentForm, self).__init__(*args, **kwargs)
        self.asso_slug = asso_slug

    def clean(self):
        cleaned_data = self.cleaned_data

        try:
            Adherent.objects.get(nom=cleaned_data['nom'],prenom=cleaned_data['prenom'],asso=cleaned_data['asso'])
        except Adherent.DoesNotExist:
            pass
        else:
            raise ValidationError('Un adhérent avec ce nom et prénom existe déjà')

        # Always return cleaned_data
        return cleaned_data

class AdherentChangeForm(forms.ModelForm):

    class Meta:
        model = Adherent
        fields = ['nom', 'prenom', 'email', ]


class AdherentChangeForm_conf66(forms.ModelForm):
    #production_ape = forms.ChoiceField(label="Production",
    #                                   help_text="Selectionner la production correspondant à votre code APE dans la liste",
    #                                  choices=list_ape)

    class Meta:
        model = Adherent
        fields = ['nom', 'prenom', 'statut', 'nom_gaec', 'email', 'production_ape', ]


class InscriptionMailForm(forms.ModelForm):
    adherent = forms.ModelChoiceField(queryset=Adherent.objects.all(), required=True, label="Adhérent", )

    class Meta:
        model = InscriptionMail
        fields = ["adherent", 'commentaire',]


    def __init__(self, asso_slug, *args, **kwargs):
        super(InscriptionMailForm, self).__init__(*args, **kwargs)
        self.fields["adherent"].choices = [('', '(Choisir un adhérent)'), ] + [(x.id, x.nom + " " + x.prenom) for x in Adherent.objects.filter(asso__slug=asso_slug).order_by("nom", "prenom") ]

class InscriptionMail_complet_Form(forms.ModelForm):
    adherent = forms.ModelChoiceField(queryset=Adherent.objects.all(), required=True, label="Adhérent", )
    email_pasadherent = forms.EmailField(required=False, help_text="Email (renseigner uniquement si ce n'est pas un adhérent)")

    class Meta:
        model = InscriptionMail
        fields = ["adherent", 'commentaire',"email_pasadherent"]

    def __init__(self, asso_slug, *args, **kwargs):
        super(InscriptionMail_complet_Form, self).__init__(*args, **kwargs)
        self.fields["adherent"].choices = [('', '(Choisir un adhérent)'), ] + [(x.id, x.nom + " " + x.prenom) for x in Adherent.objects.filter(asso__slug=asso_slug).order_by("nom", "prenom") ]

class InscriptionMail_Mail_Form(forms.ModelForm):

    class Meta:
        model = InscriptionMail
        fields = [ "email_pasadherent", 'commentaire',]


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

    def __init__(self, asso_slug, *args, **kwargs):
        super(InscriptionMail_listeAdherent_Form, self).__init__(*args, **kwargs)
        self.fields["liste_diffusion"].choices = [('', '(Choisir une liste de diffusion)'), ] + [(x.id, x.nom) for x in ListeDiffusion.objects.filter(asso__slug=asso_slug).order_by("nom", "prenom") ]



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


    def __init__(self, request, *args, **kwargs):
        super(ProjetPhoning_form, self).__init__(*args, **kwargs)
        self.fields["asso"].choices = [('', '(Choisir un groupe)'), ] + [(x.id, x.nom) for x in Asso.objects.all().order_by("nom") if request.user.estMembre_str(x.slug)]

