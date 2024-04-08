from django.contrib import admin
from .models import Adherent, Adhesion, InscriptionMail, ListeDiffusionConf


class Adherent_Admin(admin.ModelAdmin):
    list_display = ('nom', 'email', 'profil')
    search_fields = ('nom', 'email', )

class Adhesion_Admin(admin.ModelAdmin):
    list_display = ('adherent', 'date_cotisation', 'montant')
    search_fields = ('adherent', )

admin.site.register(Adherent, Adherent_Admin)
admin.site.register(Adhesion, Adhesion_Admin)
admin.site.register(InscriptionMail)
admin.site.register(ListeDiffusionConf)
