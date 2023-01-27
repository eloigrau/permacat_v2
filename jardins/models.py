from django.db import models
from django.urls import reverse
from django.utils import timezone
from taggit.managers import TaggableManager
import uuid

class Choix():
    type_jardin = ('0', 'Partagé'), ('1', 'Privé')

class DBRang_inpn(models.Model):
    RG_LEVEL = models.IntegerField()
    RANG = models.CharField(max_length=5)
    DETAIL = models.CharField(max_length=30)
    DETAIL_EN = models.CharField(max_length=30)

    def __str__(self):
        return str(self.DETAIL)

class DBStatut_inpn(models.Model):
    ORDRE = models.CharField(max_length=4)
    STATUT = models.CharField(max_length=2)
    DESCRIPTION = models.CharField(max_length=150)
    DEFINITION = models.TextField(null=True)

    def __str__(self):
        return self.DESCRIPTION + " (" + self.DEFINITION + ")"

class DBHabitat_inpn(models.Model):
    HABITAT = models.IntegerField()
    LB_HABITAT = models.TextField(null=True)
    DEFINITION = models.TextField(null=True)

    def __str__(self):
        return self.LB_HABITAT + " (" + self.DEFINITION + ")"

class DBVern_inpn(models.Model):
    CD_VERN = models.IntegerField(unique=True)
    CD_NOM = models.IntegerField()
    LB_VERN = models.TextField(null=True, blank=True)
    NOM_VERN_SOURCE = models.CharField(max_length=400)
    LANGUE = models.CharField(max_length=400)
    ISO639_3 = models.CharField(max_length=400)
    PAYS = models.CharField(max_length=400)

    def __str__(self):
        return str(self.LB_VERN)


class DB_importeur(models.Model):
    nom = models.CharField(max_length=15)
    texte = models.TextField(blank=True, null=True, )
    lg_debut = models.IntegerField(default=0)
    lg_fin = models.IntegerField(default=0)

    def __str__(self):
        return str(self.lg_debut) + " fin " + str(self.lg_fin)


class Plante(models.Model):
    REGNE = models.CharField(max_length=15)
    PHYLUM = models.CharField(max_length=30)
    CLASSE = models.CharField(max_length=50)
    ORDRE = models.CharField(max_length=50)
    FAMILLE = models.CharField(max_length=50)
    SOUS_FAMILLE = models.CharField(max_length=50)
    TRIBU = models.CharField(max_length=50)
    GROUP1_INPN = models.CharField(max_length=20)
    GROUP2_INPN = models.CharField(max_length=20)
    GROUP3_INPN = models.CharField(max_length=20)
    CD_NOM = models.IntegerField(unique=True, primary_key=True)
    CD_TAXSUP = models.CharField(max_length=8)
    CD_SUP = models.CharField(max_length=8)
    CD_REF = models.IntegerField()
    RANG = models.CharField(max_length=4)
    LB_NOM = models.CharField(max_length=200) #Nom scientifique
    LB_AUTEUR = models.CharField(max_length=200, null=True)
    NOM_COMPLET = models.TextField(null=True)
    NOM_COMPLET_HTML = models.TextField(null=True)
    NOM_VALIDE = models.CharField(max_length=250)
    NOM_VERN = models.CharField(max_length=350)
    NOM_VERN_ENG = models.CharField(max_length=250)
    HABITAT = models.CharField(max_length=40)
    FR = models.CharField(max_length=2)
    GF = models.CharField(max_length=2)
    MAR = models.CharField(max_length=2)
    GUA = models.CharField(max_length=2)
    SM = models.CharField(max_length=2)
    SB = models.CharField(max_length=2)
    SPM = models.CharField(max_length=2)
    MAY = models.CharField(max_length=2)
    EPA = models.CharField(max_length=2)
    REU = models.CharField(max_length=2)
    SA = models.CharField(max_length=2)
    TA = models.CharField(max_length=2)
    TAAF = models.CharField(max_length=2)
    PF = models.CharField(max_length=2)
    NC = models.CharField(max_length=2)
    WF = models.CharField(max_length=2)
    CLI = models.CharField(max_length=2)
    URL = models.CharField(max_length=200)
    infos_supp = models.TextField(null=True)


    def __str__(self):
        return self.NOM_VERN

    @property
    def get_nom_espece(self):
        return self.NOM_VERN + ", " + self.LB_NOM

    @property
    def get_inpi_url(self):
        return self.URL

    @property
    def get_habitat(self):
        return DBHabitat_inpn.objects.get(HABITAT=self.HABITAT)

    @property
    def get_rang(self):
        return str(DBRang_inpn.objects.get(RANG=self.RANG))

    @property
    def get_nomvern(self):
        try:
            return DBVern_inpn.objects.get(CD_NOM=self.CD_NOM)
        except:
            return ""

    def get_absolute_url(self):
        return reverse('jardins:voir_plante', kwargs={'cd_nom':self.CD_NOM})

    @property
    def get_info_supp_html(self):
        return "; ".join([" <a href='"+str(x)+"' target=_blank>"+str(i)+"</a>" for i, x in enumerate(self.infos_supp.split('; '))])


    @property
    def get_info_supp_html2(self):
        if not self.infos_supp:
            return
        return [str(x) for x in self.infos_supp.split('; ') if x]


class Jardin(models.Model):
    plante = models.ForeignKey(Plante, on_delete=models.CASCADE)
