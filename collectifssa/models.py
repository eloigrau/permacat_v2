# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

# Create your models here.
class Message_collectifssa(models.Model):
    email = models.EmailField(verbose_name=_("Email"))
    nom = models.CharField(max_length=250, verbose_name=_("Nom prénom / Raison sociale"),)
    msg = models.TextField(verbose_name=_("Message"), )
    date = models.DateTimeField(verbose_name=_("Date"), default=timezone.now)
    commentaire = models.TextField(verbose_name=_("Commentaire (interne)"), blank=True, null=True)

    def __str__(self):
        return self.nom + ", " + self.email + "; " + self.msg


    def get_absolute_url(self):
        return reverse('collectifssa:voirMessages')

    @property
    def get_comm_editurl(self):
        return reverse('collectifssa:modifierComm_msg', kwargs={'pk':self.pk})

class InscriptionCLA(models.Model):
    TYPE_ATELIERS = [
        ('cla', 'Création CLA'),
        ('formation_1', 'Formation 1 : SSA, principes et exemples (5/12/2026)'),
        ('formation_2', 'Formation 2 : Démocratie et Gouvernance (19/12/2026)'),
        ('autre', 'Autre'),
    ]

    email = models.EmailField(verbose_name=_("Email"))
    nom = models.CharField(max_length=250, verbose_name=_("Nom prénom / Raison sociale"),)
    msg = models.TextField(verbose_name=_("Message (facultatif)"), null=True, blank=True)
    date = models.DateTimeField(verbose_name=_("Date"), auto_now_add=True)
    commentaire = models.TextField(verbose_name=_("Commentaire (interne)"), blank=True, null=True)
    type_atelier = models.CharField(max_length=30, choices=TYPE_ATELIERS)

    def __str__(self):
        return self.nom + ", " + self.email + "; " + str(self.msg)

    def get_absolute_url(self):
        return reverse('collectifssa:voirMessages')

    @property
    def get_comm_editurl(self):
        return reverse('collectifssa:modifierComm_cla', kwargs={'pk':self.pk})

class Covoit(models.Model):
    nom = models.CharField(max_length=250, verbose_name=_("Nom prénom"),)
    villeDepart = models.CharField(max_length=100, verbose_name=_("Ville de départ"),)
    telephone = models.CharField(max_length=25, verbose_name=_("Téléphone"),)
    msg = models.TextField(verbose_name=_("Message (facultatif)"), null=True, blank=True )
    date = models.DateTimeField(verbose_name=_("Date"), default=timezone.now)
    type_atelier = models.CharField(max_length=30, choices=InscriptionCLA.TYPE_ATELIERS)

    BESOINS = (
        ('0', "Je cherche une place dans une voiture"),
        ('1', "J'ai 1 place dans ma voiture"),
        ('2', "J'ai 2 places dans ma voiture"),
        ('3', "J'ai 3 places dans ma voiture"),
        ('4', "J'ai 4 (ou plus) places dans ma voiture"),
    )
    besoin = models.CharField(max_length=1, choices=BESOINS, verbose_name=_("Je propose / j'ai besoin de..."),)


    def __str__(self):
        return self.nom + ", " + str(self.msg)