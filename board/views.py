import json
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .models import ProjetBoard, Colonne, Tache
from .forms import TacheForm, ProjetBoardForm
from bourseLibre.utils import testIsMembreAsso_bool
from bourseLibre.models import Asso
from django.http import HttpResponseForbidden


def testMembreAsso(request):
    if "asso_slug" in request.session:
        asso_slug = request.session["asso_slug"]
    else:
        asso_slug = 'public'

    if not testIsMembreAsso_bool(request, asso_slug):
        return HttpResponseForbidden("Désolé, vous n'avez pas l'autorisation ")

    return Asso.objects.get(slug=asso_slug)

@login_required
def liste_projets(request):
    asso = testMembreAsso(request)
    projets = ProjetBoard.objects.filter(asso=asso)
    return render(request, 'board/liste_projets.html', {'projets': projets})


@login_required
def detail_projetboard(request, projet_id):
    projet = get_object_or_404(ProjetBoard, id=projet_id)
    colonnes = projet.colonnes.all() #.prefetch_related('taches__assignes').all()

    if request.method == 'POST':
        form = TacheForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('board:detail_projet', projet_id=projet.id)
    else:
        form = TacheForm()
        # Filtrer les colonnes et membres appartenant uniquement à ce projet
        form.fields['colonne'].queryset = colonnes
        #if projet.membres.exists():
        #    form.fields['assignes'].queryset = projet.membres.all()

    return render(request, 'board/detail_projet.html', {
        'projet': projet,
        'colonnes': colonnes,
        'form': form,
    })


@login_required
@require_POST
def deplacer_tache_post(request, tache_id, colonne_id):
    tache = get_object_or_404(Tache, id=tache_id)
    nouvelle_colonne = get_object_or_404(Colonne, id=colonne_id)
    tache.colonne = nouvelle_colonne
    tache.save()
    return redirect('board:detail_projet', projet_id=nouvelle_colonne.projet.id)

@require_POST
@login_required
def deplacer_tache(request):
    try:
        data = json.loads(request.body)
        tache_id = data.get('tache_id')
        nouvelle_colonne_id = data.get('colonne_id')
        ordre_taches = data.get('ordre_taches', [])

        tache = get_object_or_404(Tache, id=tache_id)
        nouvelle_colonne = get_object_or_404(Colonne, id=nouvelle_colonne_id)

        # Mise à jour de la colonne de la tâche déplacée
        tache.colonne = nouvelle_colonne
        tache.save()

        # Mise à jour de l'ordre de toutes les cartes dans la colonne de destination
        for index, tid in enumerate(ordre_taches):
            Tache.objects.filter(id=tid).update(ordre=index)

        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)


@login_required
def creer_projetboard(request):
    asso = testMembreAsso(request)
    if request.method == 'POST':
        form = ProjetBoardForm(request.POST)
        if form.is_valid():
            form.instance.asso = asso
            projet = form.save()
            # Création automatique des colonnes par défaut façon Trello
            colonnes_defaut = ["À faire", "En cours", "Terminé"]
            for index, titre in enumerate(colonnes_defaut):
                Colonne.objects.create(projet=projet, titre=titre, ordre=index)
            return redirect('board:detail_projet', projet_id=projet.id)
    else:
        form = ProjetBoardForm()
    return render(request, 'board/form_projetboard.html', {'form': form, 'titre': 'Créer un nouveau projet'})

@login_required
def modifier_projetboard(request, projet_id):
    projet = get_object_or_404(ProjetBoard, id=projet_id)
    if not testIsMembreAsso_bool(request, projet.asso.slug):
        return HttpResponseForbidden("Désolé, vous n'avez pas l'autorisation ")

    if request.method == 'POST':
        form = ProjetBoardForm(request.POST, instance=projet)
        if form.is_valid():
            form.save()
            return redirect('board:detail_projet', projet_id=projet.id)
    else:
        form = ProjetBoardForm(instance=projet)
    return render(request, 'board/form_projetboard.html', {'form': form, 'titre': f'Modifier le projet : {projet.nom}'})

@require_POST
@login_required
def supprimer_projetboard(request, projet_id):
    projet = get_object_or_404(ProjetBoard, id=projet_id)
    if not testIsMembreAsso_bool(request, projet.asso.slug):
        return HttpResponseForbidden("Désolé, vous n'avez pas l'autorisation ")
    projet.delete()
    return redirect('board:liste_projets')


