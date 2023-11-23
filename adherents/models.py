
from django.db import models
from bourseLibre.models import Profil, Adresse
from blog.models import Article
import simplejson
from django.urls import reverse
from django.utils import timezone
import uuid


class Choix():
    statut = ('0', 'adherent')

class Adherent(models.Model):
    profil = models.ForeignKey(Profil, on_delete=models.SET_NULL, null=True)
    nom = models.CharField(verbose_name="Nom ", max_length=120)
    prenom = models.CharField(verbose_name="Prénom ", max_length=120, blank=True)
    statut = models.CharField(verbose_name="Statut d'agriculteur (AP pour 'a titre pincipal', CS pour 'cotisant solidaire')", max_length=120)
    adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE,)
    email = models.EmailField(verbose_name="Email", blank=True)

    def __str__(self):
        #profil = " (" + str(self.profil)+")" if self.profil else ""
        return self.nom + " " + self.prenom

    def get_absolute_url(self):
        return reverse('adherents:adherent_detail', kwargs={'pk': self.pk})

    def get_adresse_str(self):
        return self.adresse.get_adresse_str
# Create your models here.

    @property
    def get_adhesions(self):
        return self.adhesion_set.all()

class Adhesion(models.Model):
    adherent = models.ForeignKey(Adherent, on_delete=models.CASCADE, verbose_name="Adhérent ")
    date_cotisation = models.DateField(verbose_name="Date de la cotisation", editable=True, auto_now_add=False)
    montant = models.CharField(max_length=50, blank=False, verbose_name="Montant de l'adhesion")
    moyen = models.CharField(max_length=50, blank=False, verbose_name="Moyen de paiement")
    detail = models.TextField(null=True, blank=True)

    def __str__(self):
        return " le " + str(self.date_cotisation) + ", " + str(self.montant) + ", " + str(self.moyen)
