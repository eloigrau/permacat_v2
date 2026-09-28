from .models import BudgetCercle, BudgetProjet, Transaction
from .forms import TransactionForm, BudgetProjetForm, TransationChangeForm, SellerForm, ProductForm, ClientForm
from django.contrib.auth.decorators import login_required
from bourseLibre.utils import testIsMembreAsso_bool
from blog.models import Projet
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.views.generic import UpdateView, DeleteView
from .models import Client, Product, Facture, FactureItem, Seller
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from bourseLibre.utils import testIsMembreAsso, testIsMembreAsso_bool, TestMembreAssoMixin, TestBureauAssoMixin, UserPassesTestMixin

@login_required
def tableau_de_bord(request):
    if not "asso_slug" in request.session:
        asso_slug = "public"
    else:
        asso_slug = request.session["asso_slug"]
    if not testIsMembreAsso_bool(request, asso_slug):
        return HttpResponseForbidden("Vous n'avez pas l'autorisation de supprimer")

    cercles = BudgetCercle.objects.filter(cercle__asso__slug=asso_slug).prefetch_related('budgetprojets__transactions').all()

    return render(request, 'compta/tableau_de_bord.html', {'cercles': cercles})


@login_required
def detail_budget(request, budget_id):
    budget = get_object_or_404(BudgetProjet, id=budget_id)
    if not testIsMembreAsso_bool(request, budget.projet.asso.slug):
        return HttpResponseForbidden("Désolé, vous n'avez pas l'autorisation ")

    request.session["asso_slug"] = budget.projet.asso.slug

    # On récupère toutes les transactions liées au projet (débits, crédits, transferts sortants)
    transactions_importantes = budget.transactions.all()

    # On récupère aussi les transferts d'argent arrivés sur ce projet
    transferts_recus = budget.transferts_recus.all()

    return render(request, 'compta/detail_budget.html', {
        'budget': budget,
        'transactions': transactions_importantes,
        'transferts_recus': transferts_recus
    })

@login_required
def ajouter_transaction(request, projet_id):
    budgetprojet = BudgetProjet.objects.get(id=projet_id)
    form = TransactionForm(budgetprojet, request.POST or None)

    if form.is_valid():
        transaction = form.save()
        return redirect('compta:detail_budget', budget_id=transaction.budget.id)
    return render(request, 'compta/ajouter_transaction.html', {'form': form, "budgetprojet":budgetprojet})



class ModifierTransaction(UpdateView):
    model = Transaction
    form_class = TransationChangeForm
    template_name_suffix = '_modifier'

    # fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']

    #def get_object(self):
    #    return Transaction.objects.get(pk=self.kwargs['transaction_pk'])

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_form(self, *args, **kwargs):
        form = super(ModifierTransaction, self).get_form(*args, **kwargs)
        #form.fields["asso"].choices = [(x.id, x.nom) for x in Asso.objects.all().order_by("id") if
        #                               self.request.user.estMembre_str(x.slug)]
        #form.fields["cercle"].choices = [(x.id, '(' + x.asso.nom +') ' + x.titre) for x in Cercle.objects.all().order_by("id") if self.request.user.estMembre_str(x.asso.slug)]

        return form


class SupprimerTransaction(DeleteView): #DeleteAccess,
    model = Transaction
    template_name_suffix = '_supprimer'

    #    fields = ['user','site_web','description', 'competences', 'adresse', 'avatar', 'inscrit_newsletter']
    def form_valid(self, form):
        success_url = self.object.budget.get_absolute_url
        self.object.delete()
        return HttpResponseRedirect(success_url)

@login_required
def ajouter_budgetProjet(request):
    if "projet_slug" in request.GET:
        projet = Projet.objects.get(slug=request.GET["projet_slug"])
        asso_slug = projet.asso.slug
    else:
        projet = None
        if "asso_slug" in request.session:
            asso_slug = request.session["asso_slug"]
        else:
            asso_slug = 'public'

    if not testIsMembreAsso_bool(request, asso_slug):
        return HttpResponseForbidden("Désolé, vous n'avez pas l'autorisation ")

    form = BudgetProjetForm(asso_slug, projet, request.POST or None)

    if form.is_valid():
        budget_projet = form.save()
        return redirect('compta:detail_budget', budget_id=budget_projet.id)

    return render(request, 'compta/ajouter_budget.html', {'form': form})


def generate_facture_pdf(request, facture_id):
    facture = get_object_or_404(Facture, pk=facture_id)

    context = {
        'facture': facture,
    }

    # Rendu du template HTML
    html_string = render_to_string('compta/facture_template_pdf.html', context)

    # Conversion en PDF via WeasyPrint
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="Facture_{facture.number}.pdf"'
    return response


from .forms import FactureForm, FactureItemFormSet
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.db import transaction

from .models import Facture, FactureItem, DocumentType

# -------------------------------------------------------------------
# LISTES & DÉTAILS (FACTURES & DEVIS)
# -------------------------------------------------------------------

class FactureListView(TestMembreAssoMixin, ListView):
    model = Facture
    template_name = 'compta/facture_list.html'
    context_object_name = 'factures'

    def get_queryset(self):
        # Filtre les factures non archivées
        return Facture.objects.filter(is_archived=False, document_type=DocumentType.INVOICE)


class QuoteListView(TestMembreAssoMixin, ListView):
    model = Facture
    template_name = 'compta/quote_list.html'
    context_object_name = 'quotes'

    def get_queryset(self):
        # Filtre les devis non archivés
        return Facture.objects.filter(is_archived=False, document_type=DocumentType.QUOTE)


class ArchivedDocumentListView(TestMembreAssoMixin, ListView):
    model = Facture
    template_name = 'compta/archived_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        return Facture.objects.filter(is_archived=True)


class DocumentDetailView(TestMembreAssoMixin, DetailView):
    model = Facture
    template_name = 'compta/document_detail.html'
    context_object_name = 'document'


# -------------------------------------------------------------------
# CRÉATION & ÉDITION
# -------------------------------------------------------------------

def create_document(request, doc_type=DocumentType.INVOICE):
    """Vue générique pour créer une facture ou un devis avec ses lignes."""
    if request.method == 'POST':
        form = FactureForm(request.POST)
        formset = FactureItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                document = form.save(commit=False)
                document.document_type = doc_type
                document.save()

                formset.instance = document
                formset.save()

            messages.success(request,
                             f"{'Facture' if doc_type == DocumentType.INVOICE else 'Devis'} créé(e) avec succès.")
            return redirect('compta:document_detail', pk=document.pk)
    else:
        form = FactureForm()
        formset = FactureItemFormSet()

    return render(request, 'compta/document_form.html', {
        'form': form,
        'formset': formset,
        'doc_type': doc_type,
        'title': f"Créer un {'devis' if doc_type == DocumentType.QUOTE else 'facture'}"
    })


def update_document(request, pk):
    """Vue pour éditer un devis ou une facture existante."""
    document = get_object_or_404(Facture, pk=pk)

    if document.is_archived:
        messages.error(request, "Un document archivé ne peut pas être modifié.")
        return redirect('compta:document_detail', pk=document.pk)

    if request.method == 'POST':
        form = FactureForm(request.POST, instance=document)
        formset = FactureItemFormSet(request.POST, instance=document)

        if form.is_valid() and formset.is_valid():
            with transaction.atomic():
                form.save()
                formset.save()
            messages.success(request, "Document mis à jour avec succès.")
            return redirect('compta:document_detail', pk=document.pk)
    else:
        form = FactureForm(instance=document)
        formset = FactureItemFormSet(instance=document)

    return render(request, 'compta/document_form.html', {
        'form': form,
        'formset': formset,
        'document': document,
        'title': f"Éditer le document {document.number}"
    })


# -------------------------------------------------------------------
# ARCHIVAGE & ACTIONS
# -------------------------------------------------------------------

def archive_document(request, pk):
    """Archive un document (soft delete)."""
    document = get_object_or_404(Facture, pk=pk)
    document.is_archived = True
    document.save()
    messages.info(request, f"Le document {document.number} a été archivé.")
    return redirect('compta:archived_list')


def unarchive_document(request, pk):
    """Restaure un document archivé."""
    document = get_object_or_404(Facture, pk=pk)
    document.is_archived = False
    document.save()
    messages.success(request, f"Le document {document.number} a été restauré.")
    return redirect('compta:document_detail', pk=document.pk)


def convert_quote_to_facture(request, pk):
    """Transforme un devis en facture."""
    quote = get_object_or_404(Facture, pk=pk, document_type=DocumentType.QUOTE)

    with transaction.atomic():
        quote.document_type = DocumentType.INVOICE
        quote.number = f"FAC-{quote.number}"  # Adapte la numérotation selon ton besoin
        quote.save()

    messages.success(request, f"Le devis a été converti en facture {quote.number}.")
    return redirect('compta:document_detail', pk=quote.pk)


# ==========================================
# VUES GESTION VENDEURS (SELLER)
# ==========================================

class SellerListView(TestMembreAssoMixin, ListView):
    model = Seller
    template_name = 'compta/seller_list.html'
    context_object_name = 'sellers'

class SellerCreateView(TestMembreAssoMixin, CreateView):
    model = Seller
    form_class = SellerForm
    template_name = 'compta/seller_form.html'
    success_url = reverse_lazy('compta:seller_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nouveau Vendeur"
        return context

class SellerUpdateView(TestMembreAssoMixin, UpdateView):
    model = Seller
    form_class = SellerForm
    template_name = 'compta/seller_form.html'
    success_url = reverse_lazy('compta:seller_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Modifier le Vendeur"
        return context


# ==========================================
# VUES GESTION PRODUITS (PRODUCT)
# ==========================================

class ProductListView(TestMembreAssoMixin, ListView):
    model = Product
    template_name = 'compta/product_list.html'
    context_object_name = 'products'

class ProductCreateView(TestMembreAssoMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'compta/product_form.html'
    success_url = reverse_lazy('compta:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nouveau Produit"
        return context

class ProductUpdateView(TestMembreAssoMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'compta/product_form.html'
    success_url = reverse_lazy('compta:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Modifier le Produit"
        return context


# ==========================================
# VUES GESTION CLIENTS (CLIENT)
# ==========================================

class ClientListView(TestMembreAssoMixin, ListView):
    model = Client
    template_name = 'compta/client_list.html'
    context_object_name = 'clients'

class ClientCreateView(TestMembreAssoMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'compta/client_form.html'
    success_url = reverse_lazy('compta:client_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nouveau Client"
        return context

class ClientUpdateView(TestMembreAssoMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'compta/client_form.html'
    success_url = reverse_lazy('compta:client_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Modifier le Client"
        return context


def acceuil(request):
    return render(request, "compta/facturation_acceuil.html")