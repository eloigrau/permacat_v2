from django.contrib import admin

from .models import DBRang_inpn, DBStatut_inpn, Plante, DBHabitat_inpn, DBVern_inpn, DB_importeur, Jardin, \
    Grainotheque, InfoGraine, Graine, RTG_import, InfoPlante

admin.site.register(Plante)
admin.site.register(DBRang_inpn)
admin.site.register(DBStatut_inpn)
admin.site.register(DBHabitat_inpn)
admin.site.register(DBVern_inpn)
admin.site.register(RTG_import)
admin.site.register(DB_importeur)
admin.site.register(Jardin)
admin.site.register(Grainotheque)
admin.site.register(Graine)

@admin.register(InfoGraine)
class Adresse_Admin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'get_plantes',)

    def get_plantes(self, obj):
        return obj.get_plantes
    get_plantes.short_description = 'plantes'
    get_plantes.admin_order_field = 'plantes'

@admin.register(InfoPlante)
class Adresse_Admin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'get_plantes',)

    def get_plantes(self, obj):
        return obj.get_plantes_de_jardin
    get_plantes.short_description = 'plantes'
    get_plantes.admin_order_field = 'plantes'