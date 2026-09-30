from django import forms
from .models import BudgetProjet, Transaction, BudgetCercle, Product, Client, RecuFiscal, AssoInfo
from blog.models import Projet, Cercle
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


from django.forms import inlineformset_factory
from .models import Facture, FactureItem

class FactureForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sélectionne le vendeur par défaut si on crée un nouveau document
        if not self.instance.pk:
            default_asso_info = AssoInfo.objects.filter(is_default=True).first()
            if default_asso_info:
                self.fields['asso_info'].initial = default_asso_info.pk

    class Meta:
        model = Facture
        fields = ['client', 'asso_info']
        widgets = {
            'number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Laissez vide pour générer automatiquement'
            }),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'asso_info': forms.Select(attrs={'class': 'form-select'}),
        }

FactureItemFormSet = inlineformset_factory(
    Facture,
    FactureItem,
    fields=['product', 'quantity', 'unit_price'],
    extra=1,
    can_delete=True,
    widgets={
        'product': forms.Select(attrs={'class': 'form-select'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'Auto'}),
    }
)


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
            'code_product': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: PRD-001'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom du produit ou service'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description optionnelle'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
        }

class FactureForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk:
            default_asso_info = AssoInfo.objects.filter(is_default=True).first()
            if default_asso_info:
                self.fields['asso_info'].initial = default_asso_info.pk

    class Meta:
        model = Facture
        fields = ['number', 'client', 'project', ]
        widgets = {
            'number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Laissez vide pour générer automatiquement'
            }),
            'client': forms.Select(attrs={'class': 'form-select'}),
            #'asso_info': forms.Select(attrs={'class': 'form-select'}),
        }

FactureItemFormSet = inlineformset_factory(
    Facture,
    FactureItem,
    fields=['product', 'quantity'],
    extra=1,
    can_delete=True,
    widgets={
        'product': forms.Select(attrs={'class': 'form-select'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
     }
)


# ==========================================
# VUES GESTION VENDEURS (SELLER)
# ==========================================

class AssoInfoListView(ListView):
    model = AssoInfo
    template_name = 'compta/asso_info_list.html'
    context_object_name = 'asso_infos'

class AssoInfoCreateView(CreateView):
    model = AssoInfo
    form_class = AssoInfoForm
    template_name = 'compta/asso_info_form.html'
    success_url = reverse_lazy('compta:asso_info_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nouveau Vendeur"
        return context

class AssoInfoUpdateView(UpdateView):
    model = AssoInfo
    form_class = AssoInfoForm
    template_name = 'compta/asso_info_form.html'
    success_url = reverse_lazy('compta:asso_info_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Modifier le Vendeur"
        return context


# ==========================================
# VUES GESTION PRODUITS (PRODUCT)
# ==========================================

class ProductListView(ListView):
    model = Product
    template_name = 'compta/product_list.html'
    context_object_name = 'products'

class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'compta/product_form.html'
    success_url = reverse_lazy('compta:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nouveau Produit"
        return context

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'compta/product_form.html'
    success_url = reverse_lazy('compta:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Modifier le Produit"
        return context


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