from django.contrib import admin
from .models import Adherent, Adhesion, InscriptionMail, ListeDiffusionConf

admin.site.register(Adherent)
admin.site.register(Adhesion)
admin.site.register(InscriptionMail)
admin.site.register(ListeDiffusionConf)
