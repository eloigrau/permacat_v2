from django.contrib import admin
from .models import Theme, AssociationSalonArticle, DocumentPartage

# Register your models here.
admin.site.register(Theme)
admin.site.register(AssociationSalonArticle)
admin.site.register(DocumentPartage)

from .models import Atelier_new, InscriptionAtelier_new, CommentaireAtelier_new

admin.site.register(Atelier_new)
admin.site.register(InscriptionAtelier_new)
admin.site.register(CommentaireAtelier_new)