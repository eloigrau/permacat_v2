from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from django.db import transaction
from django.db.models import Sum
from .models import MembreSSA, CompteMonnaieLocale, Transaction, JournalDividendeUniversel

TAUX_CROISSANCE_QUOTIDIEN = Decimal('0.00026116')
DU_AMORCAGE = Decimal('10.00')


def calculer_prochain_du():
    cocreateurs = MembreSSA.objects.filter(est_cocreateur_du=True, user__is_active=True)
    nb_membres = cocreateurs.count()

    if nb_membres == 0:
        return Decimal('0.00'), Decimal('0.00'), 0

    # Somme uniquement sur la devise JUNE !
    masse_totale = CompteMonnaieLocale.objects.filter(devise='JUNE').aggregate(
        total=Sum('solde')
    )['total'] or Decimal('0.00')

    if masse_totale <= Decimal('0.00'):
        du_unitaire = DU_AMORCAGE
    else:
        du_brut = TAUX_CROISSANCE_QUOTIDIEN * (masse_totale / Decimal(nb_membres))
        du_unitaire = max(
            Decimal('0.01'),
            du_brut.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        )

    return du_unitaire, masse_totale, nb_membres


def distribuer_dividende_universel(date_cible=None):
    if date_cible is None:
        date_cible = timezone.localdate()

    if JournalDividendeUniversel.objects.filter(date_du=date_cible).exists():
        return None, f"Le Dividende Universel a déjà été versé pour le {date_cible}."

    du_unitaire, masse_avant, nb_membres = calculer_prochain_du()

    if nb_membres == 0 or du_unitaire <= 0:
        return None, "Aucun membre co-créateur actif."

    cocreateurs = MembreSSA.objects.filter(est_cocreateur_du=True, user__is_active=True)

    with transaction.atomic():
        for membre_ssa in cocreateurs:
            compte_june = membre_ssa.get_compte('JUNE')
            Transaction.objects.create(
                emetteur=None,
                destinataire=compte_june,
                devise='JUNE',
                montant=du_unitaire,
                type_transaction='CREATION_DU',
                libelle=f"Dividende Universel du {date_cible:%d/%m/%Y}"
            )

        journal = JournalDividendeUniversel.objects.create(
            date_du=date_cible,
            masse_monetaire_avant=masse_avant,
            nombre_cocreateurs=nb_membres,
            montant_du_unitaire=du_unitaire,
            masse_creee_totale=du_unitaire * Decimal(nb_membres)
        )

    return journal, f"DU de {du_unitaire} Ğ1 versé à {nb_membres} membres."