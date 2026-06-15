from django.contrib import admin
from .models import BudgetCercle, BudgetProjet, Transaction


admin.site.register(BudgetProjet)
admin.site.register(Transaction)
admin.site.register(BudgetCercle)

