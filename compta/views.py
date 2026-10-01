from .models import BudgetCercle, BudgetProjet, Transaction
from .forms import TransactionForm, BudgetProjetForm, TransationChangeForm, ClientForm, AssoInfoForm, ProductForm
from django.contrib.auth.decorators import login_required
from blog.models import Projet
from django.http import HttpResponseForbidden
from django.shortcuts import HttpResponseRedirect
from django.views.generic import UpdateView, DeleteView
from .models import Client, Product, AssoInfo
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from bourseLibre.utils import testIsMembreAsso_bool, TestMembreAssoMixin, TestBureauAssoMixin, UserPassesTestMixin
from .models import RecuFiscal
from bourseLibre.models import Asso
from .forms import RecuFiscalForm

from .forms import FactureForm, FactureItemFormSet, FactureStatutForm
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib import messages
from django.db import transaction

from .models import Facture, DocumentStatus, DocumentType, FactureItem

# -----------------------
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


# -------------------------------------------------------------------
# LISTES & DÉTAILS (FACTURES & DEVIS)
# -------------------------------------------------------------------

class FactureListView(TestMembreAssoMixin, ListView):
    model = Facture
    template_name = 'compta/facture_list.html'
    context_object_name = 'factures'

    def get_queryset(self):
        # Filtre les factures non archivées
        return Facture.objects.filter(asso=self.asso).order_by("-document_type", "-created_at")


class DevisListView(TestMembreAssoMixin, ListView):
    model = Facture
    template_name = 'compta/devis_list.html'
    context_object_name = 'deviss'

    def get_queryset(self):
        # Filtre les devis non archivés
        return Facture.objects.filter(is_archived=False, document_type=DocumentType.DEVIS)


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
#
@login_required
def create_document(request, doc_type=DocumentType.FACTURE):
    """Vue générique pour créer une facture ou un devis avec ses lignes."""
    form = FactureForm(request.POST or None)
    formset = FactureItemFormSet(request.POST or None, asso_slug=request.session["asso_slug"])

    if form.is_valid() and formset.is_valid():
        with transaction.atomic():
            asso = Asso.objects.get(slug=request.session["asso_slug"])
            asso_info, created = AssoInfo.objects.get_or_create(asso__slug=request.session["asso_slug"],
                                                                asso=asso,
                                                                is_default=True)
            if created:
                asso_info.name = asso.nom
                asso_info.save()
            document = form.save(asso_info, doc_type)

            formset.instance = document
            formset.save()

        messages.success(request, f"{'Facture' if doc_type == DocumentType.FACTURE else 'Devis'} créé(e) avec succès.")
        return redirect('compta:document_detail', pk=document.pk)

    return render(request, 'compta/document_form.html', {
        'form': form,
        'formset': formset,
        'doc_type': doc_type,
        'title': f"Créer un {'devis' if doc_type == DocumentType.DEVIS else 'facture'}"
    })


def update_document(request, pk):
    """Vue pour éditer un devis ou une facture existante."""
    document = get_object_or_404(Facture, pk=pk)

    if document.is_archived:
        messages.error(request, "Un document archivé ne peut pas être modifié.")
        return redirect('compta:document_detail', pk=document.pk)

    form = FactureForm(request.POST or None, instance=document)
    formset = FactureItemFormSet(request.POST or None, instance=document)

    if form.is_valid() and formset.is_valid():
        with transaction.atomic():
            asso = Asso.objects.get(slug=request.session["asso_slug"])
            asso_info, created = AssoInfo.objects.get_or_create(asso__slug=request.session["asso_slug"],
                                                                asso=asso,
                                                                is_default=True)
            form.save(asso_info, document.document_type)
            formset.save()
        messages.success(request, "Document mis à jour avec succès.")
        return redirect('compta:document_detail', pk=document.pk)

    return render(request, 'compta/document_form.html', {
        'form': form,
        'formset': formset,
        'document': document,
        'title': f"Éditer le document {document.number}"
    })


def document_update_statut(request, pk):
    """Vue pour éditer un devis ou une facture existante."""
    document = get_object_or_404(Facture, pk=pk)

    form = FactureStatutForm(request.POST or None, instance=document)

    if form.is_valid() :
        form.save()
        messages.success(request, "Document mis à jour avec succès.")
        return redirect('compta:document_detail', pk=document.pk)

    return render(request, 'compta/document_statut_form.html', {
        'form': form,
        'document': document,
        'title': f"Changer le statut du document {document.number}"
    })
# -------------------------------------------------------------------
# ARCHIVAGE & ACTIONS
# -------------------------------------------------------------------

def archive_document(request, pk):
    """Archive un document (soft delete)."""
    document = get_object_or_404(Facture, pk=pk)
    document.is_archived = True
    document.save(document.asso_info, document.document_type)
    messages.info(request, f"Le document {document.number} a été archivé.")
    return redirect('compta:archived_list')


def unarchive_document(request, pk):
    """Restaure un document archivé."""
    document = get_object_or_404(Facture, pk=pk)
    document.is_archived = False
    document.save()
    messages.success(request, f"Le document {document.number} a été restauré.")
    return redirect('compta:document_detail', pk=document.pk)


def convert_devis_to_facture(request, pk):
    """Transforme un devis en facture."""
    devis = get_object_or_404(Facture, pk=pk, document_type=DocumentType.DEVIS)
    new_facture = Facture(client=devis.client, project=devis.project,
                          status=DocumentStatus.DRAFT, date_echeance=devis.date_echeance,
                          is_archived=True
                          )
    new_facture.save(asso_info=devis.asso_info, doc_type=DocumentType.FACTURE,)
    for p in devis.items.all():
        item = FactureItem.objects.create(facture=p.facture, product=p.product,quantity=p.quantity, unit_price=p.unit_price )
        new_facture.items.add(item)
    new_facture.save()
    devis.is_archived = True
    devis.facture_link = new_facture.get_absolute_url()
    devis.save()

    messages.success(request, f"Le devis a été converti en facture {devis.number} -> {new_facture.number} et archivé.")
    return redirect('compta:document_detail', pk=new_facture.pk)


def dupliquer_document(request, pk):
    """Transforme un devis en facture."""
    devis = get_object_or_404(Facture, pk=pk)
    new_facture = Facture(client=devis.client, project=devis.project,
                          status=DocumentStatus.DRAFT, date_echeance=devis.date_echeance,
                          is_archived=False
                          )
    new_facture.save(asso_info=devis.asso_info, doc_type=devis.document_type)
    for p in devis.items.all():
        item = FactureItem.objects.create(facture=p.facture, product=p.product,quantity=p.quantity, unit_price=p.unit_price )
    new_facture.save()

    messages.success(request, f"Le <a href='"+ devis.get_absolute_url() + f"'>document {devis.number} </a> a été dupliqué {new_facture.number}</a>.")
    return redirect('compta:document_detail', pk=new_facture.pk)

# ==========================================
# VUES GESTION VENDEURS (ASSO)
# ==========================================

class AssoInfoListView(TestMembreAssoMixin, ListView):
    model = AssoInfo
    template_name = 'compta/asso_info_list.html'
    context_object_name = 'asso_infos'

    def get_queryset(self):
        return AssoInfo.objects.filter(asso=self.asso).order_by("asso__nom", "name")

class AssoInfoCreateView(TestMembreAssoMixin, CreateView):
    model = AssoInfo
    form_class = AssoInfoForm
    template_name = 'compta/asso_info_form.html'
    success_url = reverse_lazy('compta:asso_info_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nouveau Vendeur"
        return context

    def form_valid(self, form):
        self.object = form.save()
        self.object.asso = self.asso
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())

class AssoInfoUpdateView(TestMembreAssoMixin, UpdateView):
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

class ProductListView(TestMembreAssoMixin, ListView):
    model = Product
    template_name = 'compta/product_list.html'
    context_object_name = 'products'

    def get_queryset(self):
        return Product.objects.filter(asso=self.asso).order_by("-code_product")


class ProductCreateView(TestMembreAssoMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'compta/product_form.html'
    success_url = reverse_lazy('compta:product_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nouveau Produit"
        return context

    def form_valid(self, form):
        self.object = form.save(asso=self.asso)
        return HttpResponseRedirect(self.get_success_url())

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

    def get_queryset(self):
        return Client.objects.filter(asso=self.asso).order_by("-code_client")


class ClientCreateView(TestMembreAssoMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = 'compta/client_form.html'
    success_url = reverse_lazy('compta:client_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nouveau Client"
        return context


    def form_valid(self, form):
        self.object = form.save(asso=self.asso)
        return HttpResponseRedirect(self.get_success_url())

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



# --- Liste des reçus ---
class RecuListView(TestMembreAssoMixin,ListView):
    model = RecuFiscal
    template_name = 'compta/recus/recu_list.html'
    context_object_name = 'recus'
    ordering = ['-date']
    paginate_by = 10


# --- Détail d'un reçu ---
class RecuDetailView(TestMembreAssoMixin,DetailView):
    model = RecuFiscal
    template_name = 'compta/recus/recu_detail.html'
    context_object_name = 'recu'


# --- Modification d'un reçu ---
class RecuUpdateView(TestMembreAssoMixin, UpdateView):
    model = RecuFiscal
    form_class = RecuFiscalForm
    template_name = 'compta/recus/recu_form.html'

    def get_success_url(self):
        return reverse_lazy('compta:recu_detail', kwargs={'pk': self.object.pk})


# --- Suppression d'un reçu ---
class RecuDeleteView(TestMembreAssoMixin,DeleteView):
    model = RecuFiscal
    template_name = 'compta/recus/recu_confirm_delete.html'
    success_url = reverse_lazy('compta:recu_list')


# --- Téléchargement PDF ---
@login_required
def telecharger_recu_pdf(request, pk):
    recu = get_object_or_404(RecuFiscal, pk=pk)
    html_string = render_to_string('compta/recus/recu_fiscal_pdf.html', {'recu': recu})
    pdf_file = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recu_fiscal_{recu.numero_recu}.pdf"'
    return response

# --- Création d'un nouveau reçu ---
class RecuCreateView(TestMembreAssoMixin, CreateView):
    model = RecuFiscal
    form_class = RecuFiscalForm
    template_name = 'compta/recus/recu_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Nouveau reçu fiscal"
        context['button_text'] = "Créer le reçu"
        return context

    def get_success_url(self):
        return reverse_lazy('compta:recu_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        self.object = form.save(asso=self.asso)
        return HttpResponseRedirect(self.get_success_url())
