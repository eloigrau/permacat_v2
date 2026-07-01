from django.contrib import admin
from .models import Article, Projet, Theme, AssociationSalonArticle, Article_recherche, DocumentPartage, ArticleLiens, ArticleLienProjet, ZoneGeo, Cercle

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


@admin.register(Cercle)
class Cercle_Admin(admin.ModelAdmin):
    list_display  = ('titre', 'asso', 'slug')
    search_fields = ('titre',)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'asso', 'categorie', 'estArchive', 'get_partagesAssotxt' )
    search_fields = ('titre', )

@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ('id', 'titre', 'asso', 'estArchive', 'ficheprojet')
    search_fields = ('titre', )
