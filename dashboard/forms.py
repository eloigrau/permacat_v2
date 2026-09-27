from django import forms
from bourseLibre.models import Asso
from dal import autocomplete
from django.utils.safestring import mark_safe
from photologue.models import Document
from blog.models import Article
import dal_select2_queryset_sequence
from dal_select2_queryset_sequence.widgets import QuerySetSequenceSelect2
from django import forms
from dal_select2_queryset_sequence.widgets import QuerySetSequenceSelect2Multiple
from dal_contenttypes.fields import GenericModelMixin
from .models import Notification
from queryset_sequence import QuerySetSequence

class ChoisirCollectifForm(forms.Form):
    asso = forms.ModelChoiceField(queryset=Asso.objects.all().order_by("id"), required=True,
                              label="", )

    def __init__(self, request, *args, **kwargs):
        super(ChoisirCollectifForm, self).__init__(*args, **kwargs)
        self.fields["asso"].choices = [('', '---'), ] + [(x.id, x.nom) for x in
                                                                         Asso.objects.all().order_by("id") if
                                                                         request.user.estMembre_str(x.slug)]


# class Groupe_rechercheForm(forms.ModelForm):
#
#     class Meta:
#         model = Article_recherche
#         fields = ("article", )
#         widgets = {
#             'article': autocomplete.ModelSelect2(url='blog:article-ac-asso')
#         }
#         help_texts = {
#             'article':  mark_safe("<p style='color:teal'>(écrire ci dessus une partie du titre de l'article recherché)</p>")
#         }
#
#     def save(self):
#         instance = super(Groupe_rechercheForm, self).save()
#         return instance



class GroupeForm(forms.ModelForm):
    # On surcharge le champ virtuel ou on crée un champ personnalisé lié à la GFK
    target_object = forms.ModelChoiceField(
        queryset=QuerySetSequence(),
        widget=QuerySetSequenceSelect2(url='dashboard:groupe-ac'),
    )

    class Meta:
        model = Notification
        fields = ['target_object']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si on édite un objet existant, on pré-remplit le champ du formulaire
        if self.instance and self.instance.pk and self.instance.target_object:
            self.fields['target_object'].initial = self.instance.target_object

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Au moment de la sauvegarde, on redistribue la valeur dans les vrais champs GFK
        instance.target_object = self.cleaned_data['target_object']
        if commit:
            instance.save()
        return instance