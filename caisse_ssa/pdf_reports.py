import os
from datetime import date
from decimal import Decimal
from django.conf import settings
from django.db.models import Sum
from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML

from .models import (
    CompteMonnaieLocale, Cotisation, Transaction,
    JournalDividendeUniversel, LieuDeVente
)


def calculer_donnees_bilan_mensuel(annee: int, mois: int):
    """Calcule les totaux comptables et extrait les mouvements d'un mois donné."""
    date_debut = date(annee, mois, 1)
    if mois == 12:
        date_fin = date(annee + 1, 1, 1)
    else:
        date_fin = date(annee, mois + 1, 1)

    transactions_mois = Transaction.objects.filter(
        date_execution__gte=date_debut,
        date_execution__lt=date_fin
    ).select_related(
        'emetteur__proprietaire__user',
        'emetteur__lieu_de_vente',
        'destinataire__proprietaire__user',
        'destinataire__lieu_de_vente'
    ).order_by('date_execution')

    cotisations_mois = Cotisation.objects.filter(
        date_versement__gte=date_debut,
        date_versement__lt=date_fin,
        validee=True
    ).select_related('membre__user').order_by('date_versement')

    journaux_du = JournalDividendeUniversel.objects.filter(
        date_du__gte=date_debut,
        date_du__lt=date_fin
    ).order_by('date_du')

    def somme_tx(devise, type_tx):
        return transactions_mois.filter(
            devise=devise, type_transaction=type_tx
        ).aggregate(total=Sum('montant'))['total'] or Decimal('0.00')

    # Synthèse JUNE (Ğ1)
    bilan_june = {
        'du_cree': somme_tx('JUNE', 'CREATION_DU'),
        'cotisations': somme_tx('JUNE', 'COTISATION'),
        'allocations_versees': somme_tx('JUNE', 'ALLOCATION'),
        'achats_alimentaires': somme_tx('JUNE', 'PAIEMENT_ACHAT'),
        'solde_caisse_centrale': CompteMonnaieLocale.get_caisse_centrale('JUNE').solde,
        'masse_totale_circulation': CompteMonnaieLocale.objects.filter(devise='JUNE').aggregate(
            total=Sum('solde')
        )['total'] or Decimal('0.00'),
    }

    # Synthèse EUROS (€)
    cotisations_euros_total = cotisations_mois.filter(devise='EUROS').aggregate(
        total=Sum('montant')
    )['total'] or Decimal('0.00')

    bilan_euros = {
        'cotisations': cotisations_euros_total,
        'allocations_versees': somme_tx('EUROS', 'ALLOCATION'),
        'achats_alimentaires': somme_tx('EUROS', 'PAIEMENT_ACHAT'),
        'reimbursements_pro': somme_tx('EUROS', 'RECONVERSION'),
        'solde_caisse_centrale': CompteMonnaieLocale.get_caisse_centrale('EUROS').solde,
    }

    # État des comptes producteurs / lieux conventionnés à la date d'édition
    lieux_etats = []
    for lieu in LieuDeVente.objects.all().order_by('nom'):
        lieux_etats.append({
            'nom': lieu.nom,
            'code': lieu.code_paiement,
            'conventionne': lieu.est_conventionne,
            'solde_june': lieu.get_compte('JUNE').solde,
            'solde_euros': lieu.get_compte('EUROS').solde,
        })

    return {
        'annee': annee,
        'mois': f"{mois:02d}",
        'date_debut': date_debut,
        'date_edition': timezone.now(),
        'bilan_june': bilan_june,
        'bilan_euros': bilan_euros,
        'lieux_etats': lieux_etats,
        'cotisations': cotisations_mois,
        'transactions': transactions_mois,
        'nb_du_verses': journaux_du.count(),
    }


def generer_pdf_bilan_mensuel(annee: int, mois: int, sauvegarder_fichier=True) -> bytes:
    """Génère le PDF en mémoire et l'archive optionnellement dans MEDIA_ROOT/bilans_ssa/."""
    context = calculer_donnees_bilan_mensuel(annee, mois)
    html_string = render_to_string('caisse/rapport_mensuel_pdf.html', context)
    pdf_bytes = HTML(string=html_string).write_pdf()

    if sauvegarder_fichier:
        dossier_archives = os.path.join(settings.MEDIA_ROOT, 'bilans_ssa', str(annee))
        os.makedirs(dossier_archives, exist_ok=True)
        chemin_fichier = os.path.join(dossier_archives, f"bilan_caisse_SSA_{annee}_{mois:02d}.pdf")
        with open(chemin_fichier, 'wb') as f:
            f.write(pdf_bytes)

    return pdf_bytes