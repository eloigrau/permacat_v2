from django import forms
from .models import BudgetProjet, Transaction, BudgetCercle, Product, Client, RecuFiscal, AssoInfo
from blog.models import Projet, Cercle
from bourseLibre.models import Asso
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView
from django.forms import inlineformset_factory
from .models import Facture, FactureItem

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
        fields = ['budget', 'type_transaction', 'budget_destination', 'libelle', 'montant', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, budgetprojet, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre le projet de destination optionnel au niveau HTML (la validation se fait côté modèle)
        self.fields['budget_destination'].required = False
        self.fields['budget'].initial = budgetprojet

class TransationChangeForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['type_transaction', 'budget_destination', 'libelle', 'montant', 'date', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'class':'datepicker form-control', })
        }


class AssoInfoForm(forms.ModelForm):
    class Meta:
        model = AssoInfo
        fields = ['name', 'siret', 'adresse','iban', 'bic', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Mon Entreprise SAS'}),
            'project': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Service Client'}),
            'siret': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '14 chiffres'}),
            'iban': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'FR76 ...'}),
            'bic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XXXXXXXXXXX'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control', 'placeholder': ''}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'unit_price']
        widgets = {
            #'code_product': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: PRD-001'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du produit ou service'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description optionnelle'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
        }

    def save(self, asso):
        self.instance.save(asso=asso)
        return super(ProductForm, self)

class FactureForm(forms.ModelForm):
    #def __init__(self, *args, **kwargs):
        #super().__init__(*args, **kwargs)
        #if not self.instance.pk and "asso_slug" in request.session:
        #self.default_asso_info, created = AssoInfo.objects.get_or_create(asso__slug=Asso.objects.get(slug=request.session["asso_slug"]), is_default=True)
            # if self.default_asso_info:
            #     self.fields['asso_info'].initial = self.default_asso_info.pk

    class Meta:
        model = Facture
        fields = ['client', 'project', 'date_echeance']
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'project': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Projet'}),
            'date_echeance': forms.DateInput(format=('%d-%m-%Y'),
                                            attrs={'class': 'form-control', 'type': 'date'}),
        }



    def save(self, asso_info, doc_type):
        self.instance.save(asso_info=asso_info, doc_type=doc_type)
        super(FactureForm, self)
        return self.instance


class LigneFactureForm(forms.ModelForm):
    class Meta:
        model = FactureItem
        fields = ['product', 'quantity']

    def __init__(self, *args, **kwargs):
        # On extrait le paramètre personnalisé 'association' s'il est fourni
        asso_slug = kwargs.pop('asso_slug', None)
        super().__init__(*args, **kwargs)

        if asso_slug:
            # Filtrage du QuerySet du champ produit
            self.fields['product'].queryset = Product.objects.filter(asso__slug=asso_slug).order_by("-code_product")


class BaseLigneFactureFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        # On récupère 'association' transmis depuis la vue
        self.asso_slug = kwargs.pop('asso_slug', None)
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        # On injecte 'association' dans chaque formulaire enfant
        kwargs['asso_slug'] = self.asso_slug
        return super()._construct_form(i, **kwargs)

FactureItemFormSet = inlineformset_factory(
    Facture,
    FactureItem,
    form=LigneFactureForm,
    formset=BaseLigneFactureFormSet,
    extra=1,
    can_delete=True,
    can_order=True,
    widgets={
        'product': forms.Select(attrs={'class': 'form-select'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
     },
   # formset=BaseInlineFilteredFormSet(asso_slug=request.session["asso_slug"]),
)



class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['code_client', 'name', 'address', 'siret']
        widgets = {
            'code_client': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: CLT-001'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom ou Raison Sociale'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Adresse complète'}),
            'siret': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '14 chiffres (optionnel)'}),
        }


    def save(self, asso):
        self.instance.save(asso=asso)
        return super(ClientForm, self)

class RecuFiscalForm(forms.ModelForm):
    class Meta:
        model = RecuFiscal
        fields = [
            'asso_info',
            'nom_donateur',
            'prenom_donateur',
            'adresse_donateur',
            'montant',
            'date',
            'type_versement',
            'description',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'asso_info': forms.Select(attrs={'class': 'form-control'}),
            'nom_donateur': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom_donateur': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse_donateur': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'type_versement': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Infos complémentaires (option)'})
        }

    def save(self, asso):
        self.instance.save(asso=asso)
        return super(RecuFiscalForm, self)
