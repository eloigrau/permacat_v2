from django.contrib import admin
from .models import Adherent, Adhesion, InscriptionMail, ListeDiffusion, ContactContact, Contact, ProjetPhoning


@admin.register(Adherent)
class Adherent_Admin(admin.ModelAdmin):
    list_display = ("asso", 'nom', 'prenom', 'email', 'profil', 'get_adhesions', 'production_ape', )
    search_fields = ('nom', 'email', )

@admin.register(Adhesion)
class Adhesion_Admin(admin.ModelAdmin):
    list_display = ('adherent', 'date_cotisation', 'montant', 'asso')
    search_fields = ('adherent__nom', 'adherent__prenom', 'adherent__profil__prenom',  'adherent__profil__nom', )

@admin.register(ContactContact)
class ContactContact_Admin(admin.ModelAdmin):
    list_display = ('profil', 'date_contact',  'contact', 'statut', 'commentaire')
    search_fields = ('profil', 'statut', 'contact', )

@admin.register(Contact)
class Contact_Admin(admin.ModelAdmin):
    list_display = ("projet", "nom", "prenom", "email", )
    search_fields = ('projet', 'nom', 'prenom', 'email', )


admin.site.register(InscriptionMail)
admin.site.register(ListeDiffusion)
admin.site.register(ProjetPhoning)
