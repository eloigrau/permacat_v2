from django.contrib import admin
from .models import Theme, AssociationSalonArticle, Article_recherche, DocumentPartage, ArticleLiens, ArticleLienProjet, ZoneGeo

# Register your models here.
admin.site.register(Theme)
admin.site.register(AssociationSalonArticle)
admin.site.register(DocumentPartage)
admin.site.register(ArticleLiens)
admin.site.register(ArticleLienProjet)
admin.site.register(ZoneGeo)
admin.site.register(Article_recherche)
