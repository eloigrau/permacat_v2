
from django.db import models
from bourseLibre.models import Profil, Adresse, Asso, LONGITUDE_DEFAUT
from django.urls import reverse

from permagora.models import LATITUDE_DEFAUT
from .constantes import dict_ape, CHOIX_STATUTS, CHOIX_MOYEN, CHOIX_CONTACTS, NB_COLORS_RANGE, RANGE_COLORS_PHONING
from django.utils import timezone
import datetime
import json

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
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, verbose_name="Groupe", null=True,)

    class Meta:
        unique_together = ('nom', 'prenom',)

    def __str__(self):
        #profil = " (" + str(self.profil)+")" if self.profil else ""
        return self.nom + " " + self.prenom

    def get_absolute_url(self):
        return reverse('adherents:adherent_detail', kwargs={'pk': self.pk})

    def get_adresse_str(self):
        return self.adresse.get_adresse_str
# Create your models here.


    @property
    def get_latitude(self):
        if hasattr(self, 'adresse') and self.adresse:
            return self.adresse.get_latitude
        return LATITUDE_DEFAUT

    @property
    def get_longitude(self):
        if hasattr(self, 'adresse') and self.adresse:
            return self.adresse.get_longitude
        return LONGITUDE_DEFAUT

    @property
    def get_adhesions(self):
        return self.adhesion_set.all()

    @property
    def get_inscriptionsMail(self):
        return self.inscriptionmail_set.all()

    def getInscriptions_listeMails_csvggl(self):
        liste = " ::: ".join(["listeDiff_" + i.liste_diffusion.nom for i in self.get_inscriptionsMail])
        an = int(datetime.date.today().year)
        for i in range(1):
            if self.adhesion_set.filter(date_cotisation__year=int(an-i)).exists():
                liste += " ::: Adhesion_" + str(an-i)
        return liste

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
    moyen = models.CharField(max_length=50, blank=False, verbose_name="Moyen de paiement",
                             choices=CHOIX_MOYEN, )
    detail = models.TextField(null=True, blank=True)
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.date_cotisation.strftime('%Y')) + ": " + str(self.montant) + " euros (" + str(self.moyen) +")"

    def get_absolute_url(self):
        return reverse('adherents:adhesion_detail', kwargs={'pk': self.pk})
    def get_update_url(self):
        return reverse('adherents:adhesion_modifier', kwargs={'pk': self.pk})
    def get_delete_url(self):
        return reverse('adherents:adhesion_supprimer', kwargs={'pk': self.pk})



class ListeDiffusion(models.Model):
    nom = models.CharField(max_length=30, blank=False, unique=True)
    date_creation = models.DateTimeField(verbose_name="Date de création", editable=False, auto_now=True)
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, verbose_name="Groupe associé", null=True,)

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

    @property
    def get_liste_adherents(self, avecMail=True):
        if avecMail:
            return [i.adherent for i in self.inscriptionmail_set.all() if "@" in i.adherent.email]
        else:
            return [i.adherent for i in self.inscriptionmail_set.all()]


class InscriptionMail(models.Model):
    liste_diffusion = models.ForeignKey(ListeDiffusion, on_delete=models.CASCADE, verbose_name="Liste de diffusion", blank=True, null=True)
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




class Comm_adherent(models.Model):
    adherent = models.ForeignKey(Adherent, on_delete=models.CASCADE, verbose_name="Adhérent")
    #auteur = models.ForeignKey(Adherent, on_delete=models.CASCADE, verbose_name="auteur")
    date_creation = models.DateTimeField(verbose_name="Date de parution", default=timezone.now)
    commentaire = models.TextField(null=True, blank=True)
    #detail = models.TextField(null=True, blank=True)
    #asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return str(self.date_creation.strftime('%d/%m/%Y')) + ": " + str(self.commentaire)

    def get_absolute_url(self):
        return self.adherent.get_absolute_url()
    def get_update_url(self):
        return reverse('adherents:comm_adherent_modifier', kwargs={'pk': self.pk})
    def get_delete_url(self):
        return reverse('adherents:comm_adherent_supprimer', kwargs={'pk': self.pk})



class ProjetPhoning(models.Model):
    asso = models.ForeignKey(Asso, on_delete=models.CASCADE, verbose_name="Groupe associé",)
    titre = models.CharField(verbose_name="Nom du projet", max_length=200, blank=True)
    date_creation = models.DateTimeField(verbose_name="Date de création", default=timezone.now)
    description = models.TextField(null=True, blank=True)


    def __str__(self):
        return str(self.titre)

    def get_absolute_url(self):
         return reverse('adherents:phoning_projet_simple', kwargs={'projet_pk':self.pk})
    def get_update_url(self):
        return reverse('adherents:phoning_projet_modifier', kwargs={'pk': self.pk})
    def get_delete_url(self):
        return reverse('adherents:phoning_projet_supprimer', kwargs={'pk': self.pk})

    def toJSON(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)

class Contact(models.Model):
    nom = models.CharField(verbose_name="Nom", max_length=120, blank=True, null=True, )
    prenom = models.CharField(verbose_name="Prénom", max_length=120, blank=True, null=True, )
    email = models.CharField(verbose_name="Email", max_length=150, blank=True, null=True, )
    adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE)
    commentaire = models.TextField(null=True, blank=True)
    adherent = models.ForeignKey(Adherent, on_delete=models.SET_NULL, verbose_name="Adhérent Conf'",  blank=True, null=True)
    date_creation = models.DateTimeField(verbose_name="Date de parution", default=timezone.now)
    projet = models.ForeignKey(ProjetPhoning, on_delete=models.SET_NULL, verbose_name="Projet associé",  blank=True, null=True,)

    def __str__(self):
        return str(self.adresse.telephone) + " (" + str(self.nom) + " " + str(self.prenom) +")"

    def get_absolute_url(self):
         return reverse('adherents:phoning_projet_courant')
    def get_update_url(self):
        return reverse('adherents:phoning_contact_modifier', kwargs={'pk': self.pk})
    def get_delete_url(self):
        return reverse('adherents:phoning_contact_supprimer', kwargs={'pk': self.pk})
    def get_delete_url2(self):
        return reverse('adherents:phoning_contact_supprimer2', kwargs={'contact_pk': self.pk})
    def get_ajoutContact_url(self):
        return reverse('adherents:phoning_contact_contact_ajout', kwargs={'contact_pk': self.pk})

    def get_contacts(self):
        return self.contactcontact_set.all()

    @property
    def get_contacts_nb(self):
        return len(self.contactcontact_set.all())

    def get_profil_username(self):
        if hasattr(self, 'profil'):
            return str(self.profil)
        else:
            return ""

    @property
    def get_background_color(self):
        length = self.get_contacts_nb
        if length<NB_COLORS_RANGE:
            return RANGE_COLORS_PHONING[length]
        else:
            return  RANGE_COLORS_PHONING[NB_COLORS_RANGE]

    @property
    def get_contacts_html(self):
        html = ""
        for c in self.get_contacts():
            html += "<li>" +str(c) + "</li> "
        return html


    @property
    def get_latitude(self):
        if hasattr(self, 'adresse') and self.adresse:
            return self.adresse.get_latitude
        return LATITUDE_DEFAUT

    @property
    def get_longitude(self):
        if hasattr(self, 'adresse') and self.adresse:
            return self.adresse.get_longitude
        return LONGITUDE_DEFAUT

class ContactContact(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, verbose_name="Contact",)
    commentaire = models.CharField(verbose_name="commentaire", max_length=200, blank=True)
    date_contact = models.DateTimeField(verbose_name="Date", default=timezone.now)
    statut = models.CharField(verbose_name="Statut", max_length=2,
                              choices=CHOIX_CONTACTS, default='0',)

    def __str__(self):
        return "[" + str(self.date_contact.strftime('%d/%m %H:%M')) + "] " + str(self.get_statut_display()) + " " + str(self.commentaire)
