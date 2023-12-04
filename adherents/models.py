
from django.db import models
from bourseLibre.models import Profil, Adresse
from blog.models import Article
import simplejson
from django.urls import reverse
from .constantes import dict_ape, CHOIX_STATUTS
from django.utils import timezone
import uuid

class Adherent(models.Model):
    profil = models.ForeignKey(Profil, on_delete=models.SET_NULL, null=True)
    nom = models.CharField(verbose_name="Nom", max_length=120)
    nom_gaec = models.CharField(verbose_name="Gaec", max_length=120, blank=True)
    prenom = models.CharField(verbose_name="Prénom", max_length=120, blank=True)
    production_ape = models.CharField(verbose_name="Production (APE) ", max_length=120, blank=True)
    statut = models.CharField(verbose_name="Statut d'agriculteur", max_length=5,
                              choices=CHOIX_STATUTS, default='0',)
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

    @property
    def get_email(self):
        if self.email:
            return self.email
        return "?"


    def get_adhesion_an(self, an):
        ad = self.adhesion_set.filter(date_cotisation__year=int(an))
        if ad:
            return ad[0]
        return Adhesion()

    @property
    def get_production_str(self):
        try:
            if self.production_ape:
                return dict_ape[self.production_ape] + " (" +self.production_ape + ")"
            else:
                return "-"
        except:
            pass
        return self.production_ape

    @property
    def get_production_str2(self):
        try:
            if self.production_ape:
                return dict_ape[self.production_ape]
            else:
                return "-"
        except:
            pass
        return self.production_ape


    @property
    def get_profil_username(self):
        if self.profil:
            return self.profil.username
        return ""


class Adhesion(models.Model):
    adherent = models.ForeignKey(Adherent, on_delete=models.CASCADE, verbose_name="Adhérent ")
    date_cotisation = models.DateField(verbose_name="Date de la cotisation", editable=True, auto_now_add=False)
    montant = models.CharField(max_length=50, blank=False, verbose_name="Montant de l'adhesion")
    moyen = models.CharField(max_length=50, blank=False, verbose_name="Moyen de paiement")
    detail = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.date_cotisation.strftime('%Y')) + ": " + str(self.montant) + " euros (" + str(self.moyen) +")"

    def get_absolute_url(self):
        return reverse('adherents:adhesion_detail', kwargs={'pk': self.pk})
    def get_update_url(self):
        return reverse('adherents:adhesion_modifier', kwargs={'pk': self.pk})
    def get_delete_url(self):
        return reverse('adherents:adhesion_supprimer', kwargs={'pk': self.pk})



class ListeDiffusionConf(models.Model):
    nom = models.CharField(max_length=30, blank=False, unique=True)
    date_creation = models.DateTimeField(verbose_name="Date de création", editable=False, auto_now=True)

    def __str__(self):
        return str(self.nom)

    def get_absolute_url(self):
        return reverse('adherents:listeDiffusion_detail', kwargs={'pk': self.pk})
    def get_update_url(self):
        return reverse('adherents:listeDiffusion_modifier', kwargs={'pk': self.pk})
    def get_delete_url(self):
        return reverse('adherents:listeDiffusion_supprimer', kwargs={'pk': self.pk})


    @property
    def get_liste_inscriptions(self):
        return self.inscriptionmail_set.all()

    @property
    def get_liste_mails(self):
        return [i.adherent.email for i in self.inscriptionmail_set.all() if "@" in i.adherent.email]

class InscriptionMail(models.Model):
    liste_diffusion = models.ForeignKey(ListeDiffusionConf, on_delete=models.CASCADE, verbose_name="Liste de diffusion", blank=True, null=True)
    date_inscription = models.DateTimeField(verbose_name="Date d'inscription", editable=False, auto_now_add=True)
    adherent = models.ForeignKey(Adherent, on_delete=models.CASCADE, verbose_name="Adhérent", blank=False, null=False)
    commentaire = models.CharField(max_length=50, blank=True)

    def __unicode__(self):
        return self.__str()

    def __str__(self):
        return str(self.liste_diffusion.nom) + ": " + str(self.get_email)

    @property
    def get_email(self):
        return self.adherent.get_email


    def get_absolute_url(self):
        return reverse('adherents:inscriptionMail_detail', kwargs={'pk': self.pk})
    def get_update_url(self):
        return reverse('adherents:inscriptionMail_modifier', kwargs={'pk': self.pk})
    def get_delete_url(self):
        return reverse('adherents:inscriptionMail_supprimer', kwargs={'pk': self.pk})

