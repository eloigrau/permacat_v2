from django import forms
from .models import Tache, ProjetBoard

class TacheForm(forms.ModelForm):
    # assignes = forms.ModelMultipleChoiceField(
    #     queryset=Profil.objects.all(),
    #     widget=forms.CheckboxSelectMultiple,
    #     required=False,
    #     label="Affecter des membres"
    # )

    class Meta:
        model = Tache
        fields = ['titre', 'description', 'colonne', 'date_limite'] #'assignes',
        widgets = {
            'date_limite': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'colonne': forms.Select(attrs={'class': 'form-select'}),
        }

class ProjetBoardForm(forms.ModelForm):
    class Meta:
        model = ProjetBoard
        fields = ['nom', 'description', 'projet']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du projet...'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description...'}),
            #'membres': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        }
