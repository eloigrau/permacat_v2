from django.contrib import admin
from .models import Theme, AssociationSalonArticle, DocumentPartage, ArticleLiens, ArticleLienProjet

# Register your models here.
admin.site.register(Theme)
admin.site.register(AssociationSalonArticle)
admin.site.register(DocumentPartage)
admin.site.register(ArticleLiens)
admin.site.register(ArticleLienProjet)
