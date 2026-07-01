from django.contrib import admin
from .models import BudgetCercle, BudgetProjet, Transaction


@admin.register(BudgetProjet)
class BudgetProjet_Admin(admin.ModelAdmin):
    list_display  = ('titre', 'projet',  'slug')
    search_fields = ('titre',)

@admin.register(Transaction)
class Transaction_Admin(admin.ModelAdmin):
    list_display  = ('libelle', 'projet', 'type_transaction', 'montant')
    search_fields = ('libelle',)

@admin.register(BudgetCercle)
class BudgetCercle_Admin(admin.ModelAdmin):
    list_display  = ('cercle', 'titre', 'slug',)
    search_fields = ('titre',)