from django import forms
from .models import BudgetProjet, Transaction

class BudgetProjetForm(forms.ModelForm):
    class Meta:
        model = BudgetProjet
        fields = ['budget_cercle', 'titre', 'description', 'actif']


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['projet', 'type_transaction', 'projet_destination', 'libelle', 'montant', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre le projet de destination optionnel au niveau HTML (la validation se fait côté modèle)
        self.fields['projet_destination'].required = False