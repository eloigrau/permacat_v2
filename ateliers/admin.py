from django.contrib import admin
from .models import Atelier, CommentaireAtelier, InscriptionAtelier

@admin.register(Atelier)
class Atelier_Admin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'asso',)
    search_fields = ('titre', 'article__titre', 'auteur__username')
    autocomplete_fields = ('article',)

admin.site.register(CommentaireAtelier)
admin.site.register(InscriptionAtelier)
