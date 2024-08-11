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
admin.site.register(InfoGraine)
admin.site.register(InfoPlante)
