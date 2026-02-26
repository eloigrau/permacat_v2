from django.contrib import admin
from .models import Theme, AssociationSalonArticle, Article_recherche, DocumentPartage, ArticleLiens, ArticleLienProjet, ZoneGeo

# Register your models here.
class LienArticleAdmin(admin.ModelAdmin):
       autocomplete_fields   = ('article',)


admin.site.register(Theme)
admin.site.register(AssociationSalonArticle, LienArticleAdmin)
admin.site.register(DocumentPartage, LienArticleAdmin)
admin.site.register(ArticleLiens, LienArticleAdmin)
admin.site.register(ArticleLienProjet, LienArticleAdmin)
admin.site.register(ZoneGeo)
admin.site.register(Article_recherche)
