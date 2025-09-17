from django.db import models
from bourseLibre.models import Profil, Adresse
from blog.models import Article
import simplejson
from django.urls import reverse
from django.utils import timezone
import uuid
from bourseLibre.models import Profil, Suivis, Asso
import math
from bourseLibre.constantes import DEGTORAD
import requests
from blog.models import Choix as Choix_global
import itertools
from django.utils.translation import gettext_lazy as _

# Create your models here.
class Choix:
    statut_projet = ('prop','Proposition de projet'), ("AGO","Projet soumise à l'AGO"), ('accep',"Accepté par l'association"), ('refus',"Refusé par l'association" ),
    type_reunion_asso = {
        "rtg": ["Réunion équipe", 'Troc de Graine', 'Atelier', 'Rencontre', 'FestiGraines', 'Visite de Jardin', 'Autre'],
        "scic": ['Cercle Ancrage', 'Cercle thématique', 'Cercle Education', 'Cercle Jardins', 'Evenement', 'Divers',],
        "conf66": ['Réunion CS', 'Evenement', 'Manifestation']
      }

    type_reunion = [(str(i), y) for i, y in enumerate([x for x in list(itertools.chain.from_iterable(type_reunion_asso.values()))])]
    type_trajet = ('0', 'Véhicule personnel'), ('1', 'Covoiturage'), ('2', 'Distanciel')
    ordre_tri_reunions = {
                        "Date <":'-start_time',
                        "Date >":'start_time',
                        "Titre":'titre',
                        "Catégorie":'categorie',
    }
    ordre_tri_ndf = {
                        "Date <":'-date_note',
                        "Date >":'date_note',
                        "Titre":'titre',
                        "Catégorie":'categorie',
                        "Auteur":'auteur',
                        "Payeur":'participant',
    }

def get_typereunion(asso):
    return [(i, j) for i, j in Choix.type_reunion if j in Choix.type_reunion_asso[asso]]


class ParticipantReunion(models.Model):
    nom = models.CharField(verbose_name=_("Nom du participant"), max_length=120)
    adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE,)
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)
    #vehicule = models.BooleanField(default=True, verbose_name=_("Est venu.e avec son véhicule"))

    def __str__(self):
        return self.nom

    def get_absolute_url(self):
        return reverse('defraiement:lireParticipant', kwargs={'id': self.id})

    def get_adresse_str(self):
        return self.adresse.get_adresse_str

    def getLatLon(self):
        return self.adresse.getLatLon()

    def getDistance(self, reunion):
        try:
            x1 = float(self.adresse.latitude)*DEGTORAD
            y1 = float(self.adresse.longitude)*DEGTORAD
            x2 = float(reunion.adresse.latitude)*DEGTORAD
            y2 = float(reunion.adresse.longitude)*DEGTORAD
            x = (y2-y1) * math.cos((x1+x2)/2)
            y = (x2-x1)

            return math.sqrt(x*x + y*y) * 6371
        except:
            return 0

    def get_url(self, reunion):
        if not self.adresse.longitude or not self.adresse.latitude:
            return ""
        try:
            latlon_1 = str(self.adresse.longitude).replace(',', '.') + "," + str(self.adresse.latitude).replace(',', '.')
            latlon_2 = str(reunion.adresse.longitude).replace(',', '.') + "," + str(reunion.adresse.latitude).replace(',',
                                                                                                     '.')
            url = "http://router.project-osrm.org/route/v1/driving/" + latlon_1 + ";" + latlon_2 + "?overview=false"
        except:
            url = ''
        return url

    def get_gmaps_url(self, reunion):
        if not self.adresse.longitude or not self.adresse.latitude:
            return ""
        try:
            latlon_1 = str(self.adresse.latitude).replace(',', '.') + "," + str(self.adresse.longitude).replace(',', '.')
            latlon_2 = str(reunion.adresse.latitude).replace(',', '.') + "," + str(reunion.adresse.longitude).replace(',','.')
            url = "https://www.google.com/maps/dir/'" + latlon_1 + "'/'" + latlon_2 +"'"
        except:
            url = ''
        return url


    def getDistance_objet(self, reunion):
        distanceObject, created = Distance_ParticipantReunion.objects.get_or_create(reunion=reunion, participant=self)
        return distanceObject

    def getDistance_route(self, reunion, recalculer=False):
        distanceObject, created = Distance_ParticipantReunion.objects.get_or_create(reunion=reunion, participant=self)
        if not recalculer:
            return float(distanceObject.getDistance())
        else:
            return float(distanceObject.calculerDistance())

    def getDistance_route_allerretour(self, reunion, recalculer=False):
        distanceObject, created = Distance_ParticipantReunion.objects.get_or_create(reunion=reunion, participant=self)
        if distanceObject.type_trajet == '0':
            return self.getDistance_route(reunion, recalculer)*2.0
        elif distanceObject.type_trajet == '1':
            return self.getDistance_route(reunion, recalculer)
        elif distanceObject.type_trajet == '2':
            return 0
        else:
            return 0

    def getDistance_routeTotale(self):
        dist = 0
        for r in self.reunion_set.all():
            dist += float(self.getDistance_route(r))
        return round(dist, 1)

    def getDistance_routeTotale_allerretour(self):
        dist = 0
        for r in self.reunion_set.all():
            dist += float(self.getDistance_route_allerretour(r))
        return round(dist, 1)

class Reunion(models.Model):
    categorie = models.CharField(max_length=30,
                                 choices=(Choix.type_reunion),
                                 default='0', verbose_name=_("Dossier"))
    titre = models.CharField(verbose_name=_("Titre de la rencontre"), max_length=120)
    slug = models.SlugField(max_length=100, default=uuid.uuid4)
    description = models.TextField(null=True, blank=True, verbose_name=_("Description / compte rendu"))
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE, null=True)
    start_time = models.DateField(verbose_name=_("Date de la rencontre"), help_text="(jj/mm/an)",
                                  default=timezone.now, blank=True, null=True)
    adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE, null=True, blank=True,)
    date_creation = models.DateTimeField(verbose_name=_("Date de parution"), default=timezone.now)
    date_modification = models.DateTimeField(verbose_name=_("Date de modification"), default=timezone.now)
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)
    article = models.ForeignKey(Article,  verbose_name=_("article lié"), on_delete=models.CASCADE, null=True, blank=True)
    estArchive = models.BooleanField(default=False, verbose_name=_("Archiver la réunion"))
    participants = models.ManyToManyField(ParticipantReunion,
                                help_text="Le participant doit etre associé à une reunion existante (sinon créez d'abord la reunion)")

    class Meta:
        ordering = ('-date_creation',)

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('defraiement:lireReunion', kwargs={'slug': self.slug})


    def est_autorise(self, user):
        return self.asso.est_autorise(user)

    @property
    def getDistanceTotale(self):
        dist = 0
        for p in self.participants.all():
            try:
                dist += p.getDistance_route_allerretour(self)
            except:
                return -1
        return round(dist, 2)

    def recalculerDistance(self):
        for p in self.participants.all():
            p.getDistance_route(self, recalculer=True)

    @property
    def get_logo_nomgroupe(self):
        return Choix_global.get_logo_nomgroupe(self.asso.slug)

    @property
    def get_logo_nomgroupe_html(self):
        return self.get_logo_nomgroupe_html_taille(18)

    def get_logo_nomgroupe_html_taille(self, taille=18):
        return "<img src='/static/" + self.get_logo_nomgroupe + "' height ='"+str(taille)+"px'/>"

class Distance_ParticipantReunion(models.Model):
    reunion = models.ForeignKey(Reunion, on_delete=models.CASCADE, null=True, blank=True, )
    participant = models.ForeignKey(ParticipantReunion, on_delete=models.CASCADE, null=True, blank=True, )
    distance = models.FloatField(blank=True, null=True, verbose_name=_("Distance aller (en km)"), help_text="Mettre juste le nombre de kilomètres (sans ajouter 'km')")
    contexte_distance = models.TextField(blank=True, null=True, verbose_name=_("Description du contexte"))
    type_trajet = models.CharField(max_length=30,
                                 choices=(Choix.type_trajet),
                                 default='0', verbose_name=_("Type de trajet"))

    class Meta:
        unique_together = (('reunion', 'participant',), )

    def get_absolute_url(self):
        return reverse('defraiement:lireReunion', kwargs={'slug': self.reunion.slug})

    def save(self, calculerDistance=False, *args, **kwargs):
        ''' On save, update timestamps '''
        retour = super(Distance_ParticipantReunion, self).save(*args, **kwargs)
        if calculerDistance or not self.distance:
            self.distance = self.calculerDistance()
        return retour

    def getDistance(self):
        if self.distance:
            try:
                return float(self.distance.replace(",", "."))
            except:
                return self.distance
        else:
            return self.calculerDistance()

    def calculerDistance(self):
        if self.type_trajet == '0':
            try:
                reponse = requests.get(self.participant.get_url(self.reunion))
                data = simplejson.loads(reponse.text)
                if data["code"] != "Ok":
                    raise Exception("erreur de calcul de trajet")
                routes = data["routes"]
                self.contexte_distance = str(routes)
                dist = 100000000
                for r in routes[0]:
                    if routes[0]["distance"] < dist:
                        dist = float(routes[0]["distance"])
                if dist == 100000000:
                    dist = -1
            except:
                dist = -1
            self.distance = str(round(dist/1000.0, 2))
            self.save(calculerDistance=False)
        elif self.type_trajet == '2':
            self.distance = 0
        else:
            self.distance = 0
        return self.distance


CHOIX_MOYEN = ("VIR", "Virement"), ("CHQ", "Chèque"), ("ESP", "Espèce"), ("HA", "HelloAsso"), ("Autre", "Autre"),

class ChoixMoyenPaiement(models.IntegerChoices):
    VIREMENT = 0, _("Virement")
    CHQ = 1, _("Chèque")
    ESPECES = 2, _("Espèce")
    AUTRE = 3, _("Autre")

class ChoixTypeNdf(models.IntegerChoices):
    ACHAT = 0, _("Achat")
    HEBERGEMENT = 1, _("Hebergement")
    RESTAU = 2, _("Restauration")
    AUTRE = 3, _("Autre")


class NoteDeFrais(models.Model):
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE, null=True)
    participant = models.ForeignKey(ParticipantReunion, on_delete=models.CASCADE, null=True, blank=True, )
    date_creation = models.DateField(verbose_name=_("Date de création"), auto_now_add=True)
    date_note = models.DateField(verbose_name=_("Date du paiement"), editable=True, auto_now_add=False)
    titre = models.CharField(max_length=120, blank=False, verbose_name=_("Titre de la note de frais"))
    categorie = models.IntegerField(blank=False, choices=ChoixTypeNdf.choices,
                                 default='0', verbose_name=_("Categorie de frais"))
    montant = models.CharField(max_length=10, blank=False, verbose_name=_("Montant de la note de frais"))
    moyen = models.IntegerField(blank=False, verbose_name=_("Moyen de paiement"), choices=ChoixMoyenPaiement.choices, )
    detail = models.TextField(null=True, blank=False)
    asso = models.ForeignKey(Asso, on_delete=models.CASCADE, null=False)

    estArchive = models.BooleanField(default=False, verbose_name=_("Archiver la Note de frais"))

    def __str__(self):
        return str(self.date_creation.strftime('%Y')) + ": " + str(self.montant) + " euros (" + str(self.moyen) + ")"

    def get_absolute_url(self):
        return reverse('defraiement:ndf_detail', kwargs={'pk': self.pk})
    def get_update_url(self):
        return reverse('defraiement:ndf_modifier', kwargs={'pk': self.pk})
    def get_delete_url(self):
        return reverse('defraiement:ndf_supprimer', kwargs={'pk': self.pk})

