# forms.py
from django import forms
from .models import Proposal
from local_summernote.widgets import SummernoteWidget


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['title', 'context', 'content']
        widgets = {
            'context': SummernoteWidget(),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class ProposalClarificationEditForm(forms.ModelForm):
    """Formulaire d'édition du contexte/titre/contenu pendant la phase de clarification."""
    class Meta:
        model = Proposal
        fields = ['title', 'context', 'content']
        widgets = {
            'context': SummernoteWidget(),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }