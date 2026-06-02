from django import forms
from bourseLibre.models import Asso

class ChoisirCollectifForm(forms.Form):
    asso = forms.ModelChoiceField(queryset=Asso.objects.all().order_by("id"), required=True,
                              label="Choisir le Collectif", )

    def __init__(self, request, *args, **kwargs):
        super(ChoisirCollectifForm, self).__init__(*args, **kwargs)
        self.fields["asso"].choices = [('', '---'), ] + [(x.id, x.nom) for x in
                                                                         Asso.objects.all().order_by("nom") if
                                                                         request.user.estMembre_str(x.slug)]
