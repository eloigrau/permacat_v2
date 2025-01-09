from django.contrib import admin
from .models import Adherent, Adhesion, InscriptionMail, ListeDiffusion, ContactContact, Contact, ProjetPhoning


@admin.register(Adherent)
class Adherent_Admin(admin.ModelAdmin):
    list_display = ('nom', 'prenom', 'email', 'profil', 'get_adhesions')
    search_fields = ('nom', 'email', )

@admin.register(Adhesion)
class Adhesion_Admin(admin.ModelAdmin):
    list_display = ('adherent', 'date_cotisation', 'montant')
    search_fields = ('adherent', )

admin.site.register(InscriptionMail)
admin.site.register(ListeDiffusion)
admin.site.register(Contact)
admin.site.register(ContactContact)
admin.site.register(ProjetPhoning)
