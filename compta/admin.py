from django.contrib import admin
from .models import BudgetCercle, BudgetProjet, Transaction
from .models import Client, Product, Facture, FactureItem, Seller

@admin.register(BudgetProjet)
class BudgetProjet_Admin(admin.ModelAdmin):
    list_display  = ('titre', 'projet',  'slug')
    search_fields = ('titre',)

@admin.register(Transaction)
class Transaction_Admin(admin.ModelAdmin):
    list_display  = ('libelle', 'budget', 'budget_destination', 'type_transaction', 'montant')
    search_fields = ('libelle',)

@admin.register(BudgetCercle)
class BudgetCercle_Admin(admin.ModelAdmin):
    list_display  = ('cercle', 'titre', 'slug',)
    search_fields = ('titre',)


class FactureItemInline(admin.TabularInline):
    model = FactureItem
    extra = 1
    fields = ('product', 'quantity', 'unit_price')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('code_client', 'name', 'siret')
    search_fields = ('code_client', 'name', 'siret')


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code_product', 'name', 'unit_price')
    search_fields = ('code_product', 'name')

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('name', 'siret', 'is_default')
    list_editable = ('is_default',)

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ('number', 'client', 'created_at', 'get_total_ht')
    search_fields = ('number', 'client__name')
    inlines = [FactureItemInline]

    def get_total_ht(self, obj):
        return f"{obj.total_ht:.2f} €"
    get_total_ht.short_description = "Total HT / TTC"