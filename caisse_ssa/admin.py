from django.contrib import admin
from .models import MembreSSA, LieuDeVente, CompteMonnaieLocale, Cotisation, Transaction, JournalDividendeUniversel


@admin.register(MembreSSA)
class MembreSSAAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'est_membre_conseil',
        'est_cotisant',
        'cotisation_mensuelle_engagee',
        'est_allocataire',
        'est_cocreateur_du'
    )
    list_filter = (
        'est_membre_conseil',
        'est_cotisant',
        'est_allocataire',
        'est_cocreateur_du'
    )
    search_fields = ('user__username', 'user__email')
    list_editable = (
        'est_membre_conseil',
        'est_cotisant',
        'est_allocataire',
        'est_cocreateur_du'
    )


@admin.register(LieuDeVente)
class LieuDeVenteAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code_paiement', 'type_lieu', 'gestionnaire', 'est_conventionne', 'date_conventionnement')
    list_filter = ('est_conventionne', 'type_lieu')
    search_fields = ('nom', 'code_paiement', 'gestionnaire__user__username')
    list_editable = ('est_conventionne',)


@admin.register(CompteMonnaieLocale)
class CompteMonnaieLocaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'devise', 'type_compte', 'proprietaire', 'lieu_de_vente', 'solde', 'date_creation')
    list_filter = ('devise', 'type_compte')
    search_fields = ('proprietaire__user__username', 'lieu_de_vente__nom')
    readonly_fields = ('date_creation',)


@admin.register(Cotisation)
class CotisationAdmin(admin.ModelAdmin):
    list_display = ('membre', 'devise', 'montant', 'moyen_paiement', 'mois_concerne', 'validee', 'date_versement')
    list_filter = ('devise', 'validee', 'moyen_paiement', 'mois_concerne')
    search_fields = ('membre__user__username',)
    readonly_fields = ('date_versement',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'devise', 'type_transaction', 'montant', 'date_execution')
    list_filter = ('devise', 'type_transaction')
    readonly_fields = ('reference', 'devise', 'emetteur', 'destinataire', 'montant', 'type_transaction', 'libelle', 'date_execution')
    search_fields = ('reference', 'libelle')


@admin.register(JournalDividendeUniversel)
class JournalDividendeUniverselAdmin(admin.ModelAdmin):
    list_display = ('date_du', 'montant_du_unitaire', 'nombre_cocreateurs', 'masse_creee_totale', 'masse_monetaire_avant')
    readonly_fields = ('date_du', 'masse_monetaire_avant', 'nombre_cocreateurs', 'montant_du_unitaire', 'masse_creee_totale', 'date_execution')