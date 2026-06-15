from django.shortcuts import render, redirect, get_object_or_404
from .models import BudgetCercle, BudgetProjet, Transaction
from .forms import TransactionForm, BudgetProjetForm
from django.contrib.auth.decorators import login_required

@login_required
def tableau_de_bord(request):
    if not "asso_slug" in  request.session:
        asso_slug = "public"
    else:
        asso_slug = request.session["asso_slug"]

    cercles = BudgetCercle.objects.filter(cercle__asso__slug=asso_slug).prefetch_related('budgetprojets__transactions').all()

    return render(request, 'compta/tableau_de_bord.html', {'cercles': cercles})


@login_required
def detail_projet(request, projet_id):
    projet = get_object_or_404(BudgetProjet, pk=projet_id)

    # On récupère toutes les transactions liées au projet (débits, crédits, transferts sortants)
    transactions_importantes = projet.transactions.all()

    # On récupère aussi les transferts d'argent arrivés sur ce projet
    transferts_recus = projet.transferts_recus.all()

    return render(request, 'compta/detail_projet.html', {
        'projet': projet,
        'transactions': transactions_importantes,
        'transferts_recus': transferts_recus
    })

@login_required
def ajouter_transaction(request, projet_id):
    form = TransactionForm(projet_id, request.POST or None)
    if form.is_valid():
        transaction = form.save()
        return redirect('compta:detail_projet', projet_id=transaction.projet.id)
    return render(request, 'compta/ajouter_transaction.html', {'form': form})

