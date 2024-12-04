from django.contrib import admin
from .models import Commentaire, Article, Evenement

# Register your models here.
admin.site.register(Evenement)
admin.site.register(Article)
admin.site.register(Commentaire)

