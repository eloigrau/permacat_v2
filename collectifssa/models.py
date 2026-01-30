# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Message_collectifssa(models.Model):
    email = models.EmailField(verbose_name=_("Email"))
    nom = models.CharField(max_length=250, verbose_name=_("Nom prénom / Raison sociale"),)
    msg = models.TextField(verbose_name=_("Message"), )

