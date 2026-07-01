from django.shortcuts import render, redirect, get_object_or_404
from .models import BudgetCercle, BudgetProjet, Transaction
from .forms import TransactionForm, BudgetProjetForm
from django.contrib.auth.decorators import login_required
from bourseLibre.utils import testIsMembreAsso_bool
from blog.models import Projet
from django.http import HttpResponseForbidden

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
def detail_projet(request, projet_id):
    budget = get_object_or_404(BudgetProjet, pk=projet_id)
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
        return redirect('compta:detail_projet', projet_id=transaction.projet.id)
    return render(request, 'compta/ajouter_transaction.html', {'form': form, "budgetprojet":budgetprojet})


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

    if not testIsMembreAsso_bool(request, projet.asso.slug):
        return HttpResponseForbidden("Désolé, vous n'avez pas l'autorisation ")

    form = BudgetProjetForm(asso_slug, projet, request.POST or None)

    if form.is_valid():
        budget_projet = form.save()
        return redirect('compta:detail_projet', projet_id=budget_projet.id)

    return render(request, 'compta/ajouter_budget.html', {'form': form})

