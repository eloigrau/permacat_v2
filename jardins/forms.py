from django import forms
from .models import Plante_recherche, Jardin, Grainotheque, PlanteDeJardin, InfoPlante, Graine, InfoGraine
from bourseLibre.models import Profil, InscritSalon, Salon
from django.utils.text import slugify
from local_summernote.widgets import SummernoteWidget
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
    #referent = forms.ChoiceField(label='Référent(.e) du jardin', required=False)

    class Meta:
        model = Jardin
        fields = ['titre', 'email_contact', 'telephone', 'categorie',  'visibilite_annuaire', 'description',  'fonctionnement', ]
        widgets = {
            'description': SummernoteWidget(),
        }

    def __init__(self, current_user, *args, **kwargs):
        super(JardinForm, self).__init__(*args, **kwargs)
   #     self.fields['referent'].choices = [(current_user.id, current_user), ] + [(u.id,u) for i, u in enumerate(Profil.objects.filter(adherent_jp=True).order_by('username')) if u != current_user]

   # def is_valid(self, *args, **kwargs):
    #    return super(JardinForm, self).is_valid(*args, **kwargs)

    def save(self, userProfile, ):
        #self.cleaned_data['referent'] = Profil.objects.get(id=self.cleaned_data['referent'])
        instance = super(JardinForm, self).save(commit=False)

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
   # referent = forms.ChoiceField(label='Référent(.e) du jardin', required=False)

    class Meta:
        model = Jardin
        fields = ['titre', 'email_contact', 'telephone', 'categorie', 'visibilite_annuaire',
                  'description', 'fonctionnement', 'permapotes_id']
        widgets = {
            'description': SummernoteWidget(),
        }

    def __init__(self, current_user, *args, **kwargs):
        super(JardinChangeForm, self).__init__(*args, **kwargs)
        #self.fields['referent'].choices = [(current_user.id, current_user), ] + [(u.id,u) for i, u in enumerate(Profil.objects.filter(adherent_jp=True).order_by('username')) if u != current_user]


class SalonJardinForm(forms.ModelForm):

    class Meta:
        model = Salon
        fields = ['titre', 'estPublic' ]

    def save(self, request, jardin):
        instance = super(SalonJardinForm, self).save(commit=False)
        instance.jardin = jardin
        instance.estPublic = False
        instance.save()
        inscrit = InscritSalon(salon=instance, profil=request.user)
        inscrit.save()
        return instance

class GrainothequeForm(forms.ModelForm):
    #referent = forms.ChoiceField(label='Référent(.e) de la grainothèque', required=False)

    class Meta:
        model = Grainotheque
        fields = [ 'titre', 'categorie', 'description', 'email_contact', 'jardin', 'visibilite_annuaire',]
        widgets = {
            'description': SummernoteWidget(),
        }

    def __init__(self, current_user, *args, **kwargs):
        super(GrainothequeForm, self).__init__(*args, **kwargs)
        #self.fields['referent'].choices = [(current_user.id, current_user), ] + [(u.id,u) for i, u in enumerate(Profil.objects.filter(adherent_jp=True).order_by('username')) if u != current_user]


    def save(self, userProfile, ):
        instance = super(GrainothequeForm, self).save(commit=False)

        max_length = Grainotheque._meta.get_field('slug').max_length
        instance.slug = orig = slugify(instance.titre)[:max_length]

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
    #referent = forms.ChoiceField(label='Référent(.e) de la grainothèque', required=False)

    class Meta:
        model = Grainotheque
        fields = ['titre', 'categorie', 'description', 'email_contact', 'visibilite_annuaire', 'jardin',]
        widgets = {
            'description': SummernoteWidget(),
        }

    def __init__(self, current_user, *args, **kwargs):
        super(GrainothequeChangeForm, self).__init__(*args, **kwargs)
       # self.fields['referent'].choices = [(current_user.id, current_user), ] + [(u.id,u) for i, u in enumerate(Profil.objects.filter(adherent_jp=True).order_by('username')) if u != current_user]


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


class PlanteDeJardinForm(forms.ModelForm):
    class Meta:
        model = PlanteDeJardin
        fields = ['nom', ]

    def save(self, jardin, infos, plante):
        instance = super(PlanteDeJardinForm, self).save(commit=False)
        instance.jardin = jardin
        instance.infos = infos
        instance.plante = plante
        instance.save()
        return instance

class InfoPlanteForm(forms.ModelForm):
    class Meta:
        model = InfoPlante
        fields = ['type_plante', 'description', ]
        widgets = {
            'description': SummernoteWidget(),
        }

class ContactParticipantsForm(forms.Form):
    msg = forms.CharField(label="Message", widget=SummernoteWidget)



