from django import forms
from .models import Plante_recherche, Jardin, Grainotheque, Choix, Graine, InfoGraine
from bourseLibre.models import Profil
from django.utils.text import slugify
from local_summernote.widgets import SummernoteWidget, SummernoteWidgetBase, SummernoteInplaceWidget
from django.urls import reverse
from bourseLibre.settings import SUMMERNOTE_CONFIG as summernote_config
from django.contrib.staticfiles.templatetags.staticfiles import static
from dal import autocomplete
import re
import itertools

class Plante_rechercheForm(forms.ModelForm):

    class Meta:
        model = Plante_recherche
        fields = ("plante", )
        widgets = {
            'plante': autocomplete.ModelSelect2(url='jardins:plante-ac')
        }

    def save(self):
        instance = super(Plante_rechercheForm, self).save()
        return instance


class JardinForm(forms.ModelForm):
    class Meta:
        model = Jardin
        fields = ['titre', 'email_contact', "referent", 'telephone', 'categorie',  'visibilite_annuaire', 'visibilite_adresse', 'description',  'fonctionnement', ]
        widgets = {
            'description': SummernoteWidget(),
        }

    def __init__(self, *args, **kwargs):
        super(JardinForm, self).__init__(*args, **kwargs)
        listeChoix = [(u.id,u) for i, u in enumerate(Profil.objects.filter(adherent_jp=True).order_by('username'))]
        listeChoix.insert(0, ("", "----------------"))
        self.fields['referent'].choices = listeChoix
        self.fields['referent'].required = False

    def save(self, userProfile, ):
        instance = super(JardinForm, self).save(commit=False)
        try:
            referent = int(self.cleaned_data['referent'])
            instance.referent = dict(self.fields['referent'].choices)[referent].username
        except:
            pass

        max_length = Jardin._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.titre)[:max_length]

        for x in itertools.count(1):
            if not Jardin.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        if len(re.findall(r"[A-Z]", instance.titre)) > 8:
            instance.titre = instance.titre.title()

        instance.auteur = userProfile
        instance.save()
        return instance


class JardinChangeForm(forms.ModelForm):
    class Meta:
        model = Jardin
        fields = ['titre', 'email_contact', 'telephone', 'categorie', 'visibilite_annuaire', 'visibilite_adresse',
                  'description', 'fonctionnement', 'permapotes_id']
        widgets = {
            'description': SummernoteWidget(),
        }

    def __init__(self, *args, **kwargs):
        super(JardinChangeForm, self).__init__(*args, **kwargs)
        listeChoix = [(u.id,u) for i, u in enumerate(Profil.objects.filter(adherent_jp=True).order_by('username'))]
        listeChoix.insert(0, ("", "----------------"))
        self.fields['referent'].choices = listeChoix
        self.fields['referent'].required = False

class GrainothequeForm(forms.ModelForm):


    class Meta:
        model = Grainotheque
        fields = [ 'titre', 'categorie', 'description', 'referent', 'email_contact', 'jardin', 'visibilite_annuaire', 'visibilite_adresse',]
        widgets = {
            'description': SummernoteWidget(),
        }

    def __init__(self, *args, **kwargs):
        super(GrainothequeForm, self).__init__(*args, **kwargs)
        listeChoix = [(u.id,u) for i, u in enumerate(Profil.objects.filter(adherent_jp=True).order_by('username'))]
        listeChoix.insert(0, ("", "----------------"))
        self.fields['referent'].choices = listeChoix
        self.fields['referent'].required = False

    def save(self, userProfile, ):
        instance = super(GrainothequeForm, self).save(commit=False)

        max_length = Grainotheque._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.titre)[:max_length]
        try:
            referent = int(self.cleaned_data['referent'])
            instance.referent = dict(self.fields['referent'].choices)[referent].username
        except:
            pass

        for x in itertools.count(1):
            if not Grainotheque.objects.filter(slug=instance.slug).exists():
                break

            # Truncate the original slug dynamically. Minus 1 for the hyphen.
            instance.slug = "%s-%d" % (orig[:max_length - len(str(x)) - 1], x)

        if len(re.findall(r"[A-Z]", instance.titre)) > 8:
            instance.titre = instance.titre.title()

        instance.auteur = userProfile
        instance.save()
        return instance


class GrainothequeChangeForm(forms.ModelForm):
    class Meta:
        model = Grainotheque
        fields = ['titre', 'categorie', 'description', 'referent', 'email_contact', 'visibilite_annuaire', 'visibilite_adresse', 'jardin',]
        widgets = {
            'description': SummernoteWidget(),
        }

    def __init__(self, *args, **kwargs):
        super(GrainothequeChangeForm, self).__init__(*args, **kwargs)
        listeChoix = [(u.id,u) for i, u in enumerate(Profil.objects.filter(adherent_jp=True).order_by('username'))]
        listeChoix.insert(0, ("", "----------------"))
        self.fields['referent'].choices = listeChoix
        self.fields['referent'].required = False

class GraineForm(forms.ModelForm):
    class Meta:
        model = Graine
        fields = ['nom', ]

    def save(self, graino, infos, plante):
        instance = super(GraineForm, self).save(commit=False)
        instance.grainotheque = graino
        instance.infos = infos
        instance.plante = plante
        instance.save()
        return instance

class InfoGraineForm(forms.ModelForm):
    class Meta:
        model = InfoGraine
        fields = [ 'date_recolte', 'stock_quantite', 'description',]
        widgets = {
            'description': SummernoteWidget(),
            'date_recolte': forms.DateInput(
            format = ('%Y-%m-%d'),
                     attrs = {'class': 'form-control',
                              'type': 'date'
                              }),
        }


class ContactParticipantsForm(forms.Form):
    msg = forms.CharField(label="Message", widget=SummernoteWidget)



