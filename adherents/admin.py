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

@admin.register(ContactContact)
class ContactContact_Admin(admin.ModelAdmin):
    list_display = ('profil', 'date_contact',  'contact', 'statut', 'commentaire')
    search_fields = ('profil', 'statut', 'contact', )

@admin.register(Contact)
class Contact_Admin(admin.ModelAdmin):
    list_display = ('profil',  "nom", "prenom", "email", "projet")
    search_fields = ('profil', 'nom', 'prenom', 'email', 'projet', )


admin.site.register(InscriptionMail)
admin.site.register(ListeDiffusion)
admin.site.register(ProjetPhoning)
