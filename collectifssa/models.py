# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Message_collectifssa(models.Model):
    email = models.EmailField(verbose_name=_("Email"))
    nom = models.CharField(max_length=250, verbose_name=_("Nom prénom / Raison sociale"),)
    msg = models.TextField(verbose_name=_("Message"), )


    def __str__(self):
        return self.nom + ", " + self.email + "; " + self.msg


class InscriptionCLA(models.Model):
    email = models.EmailField(verbose_name=_("Email"))
    nom = models.CharField(max_length=250, verbose_name=_("Nom prénom / Raison sociale"),)
    msg = models.TextField(verbose_name=_("Message (facultatif)"), null=True, blank=True )

    def __str__(self):
        return self.nom + ", " + self.email + "; " + self.msg

class Covoit(models.Model):
    nom = models.CharField(max_length=250, verbose_name=_("Nom prénom"),)
    villeDepart = models.CharField(max_length=100, verbose_name=_("Ville de départ"),)
    telephone = models.CharField(max_length=25, verbose_name=_("Téléphone"),)
    msg = models.TextField(verbose_name=_("Message (facultatif)"), null=True, blank=True )
    BESOINS = (
        ('0', "Je cherche une place dans une voiture"),
        ('1', "J'ai 1 place dans ma voiture"),
        ('2', "J'ai 2 places dans ma voiture"),
        ('3', "J'ai 3 places dans ma voiture"),
        ('4', "J'ai 4 (ou plus) places dans ma voiture"),
    )
    besoin = models.CharField(max_length=1, choices=BESOINS, verbose_name=_("Je propose / j'ai besoin de..."),)


    def __str__(self):
        return self.nom + ", " + self.email + "; " + self.msg