from django import forms
from .models import BudgetProjet, Transaction, BudgetCercle
from blog.models import Projet, Cercle

class BudgetProjetForm(forms.ModelForm):
    class Meta:
        model = BudgetProjet
        fields = ['projet', 'titre', 'description']

    def __init__(self, asso_slug, projet, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre le projet de destination optionnel au niveau HTML (la validation se fait côté modèle)
        self.fields['projet'].choices = [(p.id, p.titre + " (Cercle " + str(p.cercle) +")") for p in Projet.objects.filter(asso__slug=asso_slug)]
        if projet:
            self.fields['projet'].initial = projet

    def save(self, ):
        instance = super(BudgetProjetForm, self).save(commit=False)
        if not instance.projet.cercle:
            instance.projet.cercle, created = Cercle.objects.get_or_create(asso=instance.asso, titre='Global')

        instance.budget_cercle, created = BudgetCercle.objects.get_or_create(cercle=instance.projet.cercle)
        instance.save()
        return instance

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['projet', 'type_transaction', 'projet_destination', 'libelle', 'montant', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, budgetprojet, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre le projet de destination optionnel au niveau HTML (la validation se fait côté modèle)
        self.fields['projet_destination'].required = False
        self.fields['projet'].initial = budgetprojet