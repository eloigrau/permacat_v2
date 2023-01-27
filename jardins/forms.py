from django import forms
from .models import Jardin
from django.utils.text import slugify
import itertools
from django_summernote.widgets import SummernoteWidget, SummernoteWidgetBase, SummernoteInplaceWidget
from django.urls import reverse
from bourseLibre.settings import SUMMERNOTE_CONFIG as summernote_config
from django.contrib.staticfiles.templatetags.staticfiles import static
from dal import autocomplete

class Plante_rechercheForm(forms.ModelForm):

    class Meta:
        model = Jardin
        fields = ("plante", )
        widgets = {
            'plante': autocomplete.ModelSelect2(url='jardins:plante-ac')
        }

    def save(self):
        instance = super(Plante_rechercheForm, self).save()
        return instance

