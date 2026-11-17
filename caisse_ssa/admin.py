from django.contrib import admin
from .models import MembreSSA, LieuDeVente, CompteMonnaieLocale, Cotisation, Transaction


@admin.register(MembreSSA)
class MembreSSAAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'cotisation_mensuelle_engagee', 'est_allocataire')
    list_filter = ('role', 'est_allocataire')
    search_fields = ('user__username', 'user__email')


@admin.register(LieuDeVente)
class LieuDeVenteAdmin(admin.ModelAdmin):
    list_display = ('nom', 'code_paiement', 'type_lieu', 'est_conventionne', 'date_conventionnement')
    list_filter = ('est_conventionne', 'type_lieu')
    search_fields = ('nom', 'code_paiement')


@admin.register(CompteMonnaieLocale)
class CompteAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_compte', 'proprietaire', 'lieu_de_vente', 'solde')


@admin.register(Cotisation)
class CotisationAdmin(admin.ModelAdmin):
    list_display = ('membre', 'montant', 'moyen_paiement', 'mois_concerne', 'validee')


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'type_transaction', 'emetteur', 'destinataire', 'montant', 'date_execution')
    list_filter = ('type_transaction',)
    readonly_fields = ('reference', 'emetteur', 'destinataire', 'montant', 'type_transaction', 'date_execution')