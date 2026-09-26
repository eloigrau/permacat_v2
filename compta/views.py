from .models import BudgetCercle, BudgetProjet, Transaction
from .forms import TransactionForm, BudgetProjetForm, TransationChangeForm
from django.contrib.auth.decorators import login_required
from bourseLibre.utils import testIsMembreAsso_bool
from blog.models import Projet
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404, HttpResponseRedirect
from django.views.generic import UpdateView, DeleteView

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

