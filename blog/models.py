from django.db import models
from bourseLibre.models import Profil, Suivis, Asso, Adresse, username_re, Salon
from photologue.models import Document
from django.urls import reverse
from django.utils import timezone, html
from actstream import action
from actstream.models import followers
from taggit.managers import TaggableManager
from photologue.models import Album
from django.utils.text import slugify
from datetime import datetime, timedelta
from django.utils.safestring import mark_safe
from webpush import send_user_notification
from django.templatetags.static import static
from jardins.models import Jardin
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _
import uuid
from adherents.models import Adhesion
from bourseLibre.settings import DATE_INPUT_FORMAT
from tinymce import models as tinymce_models

class Choix:
    statut_projet = ('prop','Proposition de projet'), ("AGO","Fiche projet soumise à l'AGO"), ('accep',"Accepté par l'association"), ('refus',"Refusé par l'association" ),
    type_projet = ('Part','Participation à un évènement'), ('AGO',"Organisation d'une AGO"), ('Projlong','Projet a long terme'), ('Projcourt','Projet a court terme'), ('Projponct','Projet ponctuel'),
    type_annonce_base = ('Annonce','Information'), ('Administratif','Organisation'), ('Agenda','Evenement / Agenda'),  ('Chantier','Atelier/Chantier participatif'),\
                   ('Documentation','Documentation'),  \
                    ('Point', 'Idée / Point de vue'),  ('Recette', 'Recette'), ('BonPlan','Bon Plan / achat groupé'), \
                     ('Divers','Divers')
    type_annonce_viure = ('Info', 'Annonce / Information'), ('Agenda', 'Agenda'), ('coordination', "Coordination"), ('reunion', "Réunions"), \
                         ('manifestations', 'Manifestations'), ('projets', 'Projets écocides')
    type_annonce_ssa = ('Info', 'Annonce / Information'), ('Agenda', 'Agenda'), ('documentation', "Documentation"), ('organisation', "Organisation du groupe"), ('Chantier','Atelier/Chantier participatif'),\
                        ('groupeW','Groupe de travail'),


    type_annonce_citealt_orga = ('orga1', "Cercle Organisation"), ('orga2', "Cercle Informatique"), ('orga3', "Cercle Communication"), ('orga4', "Cercle Animation"),  ('orga5', "Cercle Médiation")
    type_annonce_citealt_themes = ('theme1', "Cercle Education"), ('theme2', "Cercle Ecolieux"), ('theme3', "Cercle Santé"), ('theme4', "Cercle Echanges"),  ('theme5', "Cercle Agriculture"),  ('theme6', "Cercle Célébration")
    type_annonce_citealt_groupes = ('groupe1', "Groupe de Perpignan"), ('groupe2', "Groupe des Albères"), ('groupe3', "Groupe des Aspres"), ('groupe4', "Groupe du Vallespir"),  ('groupe5', "Groupe du Ribéral"),  ('groupe7', "Groupe du Conflent"),('groupe6', "Groupe de la côte"),
    type_annonce_citealt_groupes_logo = {'groupe1':'img/cercles/cercleBleu.png','groupe2':'img/cercles/cercleRouge.png','groupe3':'img/cercles/cercleVert.png','groupe4':'img/cercles/cercleBleuClair.png','groupe5':'img/cercles/cercleOrange.png','groupe6':'img/cercles/cercleBlanc.png','groupe7':'img/cercles/cercleJaune.png',}
    type_annonce_citealt = type_annonce_citealt_orga + type_annonce_citealt_themes + type_annonce_citealt_groupes

    type_annonce_projets = ('Altermarché', 'Altermarché'),  ('Ecovillage', 'Ecovillage'), \
                   ('Jardin', 'Jardins partagés'), ('ChantPossible', 'Ecolieu Chant des possibles'), ('BD_Fred', 'Les BD de Frédéric')  #('KitPerma', 'Kit Perma Ecole'),
    type_annonce_bzz2022 = ('AgendaBzz', 'AgendaBzz'),  ('Documentation', 'Documentation'), ('rendez-vous', 'Rendez-vous'),
    type_annonce_jp_base = ('Discu','Information'), ('Organisation', 'Organisation'),  \
                   ('Documentation','Documentation'), ('PeupleArbres', "Peuple de l'Arbre"), ('Autre','Autre'),

    type_annonce_jp = type_annonce_jp_base + tuple([('jardin_' + str(i), 'Jardin_' + str(i)) for i in range(100)])

    type_annonce_scic = ('Annonce','Information'), ('Administratif','Organisation'), ('Agenda','Agenda'),  ('Avantproj','Avant Projet'),  ('Cercle0',"Cercle d'Ancrage"),('Cercle1',"Cercle Education"),\
                        ('Cercle2',"Cercle Jardins"),('Cercle3',"Cercle Thématique"),('Cercle4',"Cercle Communication"),\
                        ('Cercle5',"Cercle Partenariat"),('Cercle6',"Cercle Evenementiel"),('tram66',"TRAM 66")

    type_annonce_ducepaj = ('Annonce','Information'), ('Administratif','Organisation'), ('Agenda','Agenda'),  ('documentation',"Documentation")

    type_annonce_conf66 = ('Annonce', 'Information'), ("Idees", "Idées"), ('administratif', 'Gestion de la conf66'), ('evenement', 'Actions/Evènement'), \
                          ("safer", "SAFER"), ("cdpnaf", "CDPNAF"), ("Commission", "Commission"), ("eau", "Eau"), ("photovolt", "Photovoltaïque")
    # ("elevage", "Elevage"),  ("viticulture", "Viticulture"),("maraichage", "Maraichage"), ("ppam","PPAM"),("arboriculture", "Arboriculture")
    type_annonce_public = type_annonce_base + type_annonce_projets + (('professionel','Activité Pro'), ('sante','Santé et Bien-être'), )
    type_annonce_asso = {
        "public": type_annonce_public,
        "pc": type_annonce_base,
        "scic": type_annonce_scic,
        "ducepaj": type_annonce_ducepaj,
        "fer": type_annonce_base,
        "rtg": type_annonce_base,
        "viure": type_annonce_viure,
        "citealt": type_annonce_base + type_annonce_citealt,
        "bzz2022": type_annonce_bzz2022,
        "jp": type_annonce_jp,
        "conf66":type_annonce_conf66,
        "ssa":type_annonce_ssa
    }

    type_annonce = type_annonce_public + type_annonce_citealt + type_annonce_viure + type_annonce_bzz2022 + type_annonce_jp + type_annonce_scic + type_annonce_conf66 + type_annonce_ssa + type_annonce_ducepaj
    couleurs_annonces = {
       # 'Annonce':"#e0f7de", 'Administratif':"#dcc0de", 'Agenda':"#d4d1de", 'Entraide':"#cebacf",
       # 'Chantier':"#d1ecdc",'Jardinage':"#fcf6bd", 'Recette':"#d0f4de", 'Bricolage':"#fff2a0",
       # 'Culture':"#ffc4c8", 'Bon_plan':"#bccacf", 'Point':"#87bfae", 'Autre':"#bcb4b4"

        'Annonce':"#d1ecdc",
        'Administratif':"#D4CF7D",
        'Agenda':"#E0E3AB",
        'Entraide':"#AFE4C1",
        'Chantier':"#fff2a0",
        'Jardi':"#B2AFE4",
        'Recette':"#d0f4de",
        'KitPerma':"#caf9b7",
        'Permaculture':"#ced2d3",
        'Bon_plan':"#349D9B",
        'Point':"#bccacf",
        'Autre':"#87bfae",
        'Ecovillage':"#cebacf",
        'Jardin':"#fffdcc",
        'Altermarché':"#daffb3",
        'Documentation':'#ddd0a8',
        'groupeW':'#AFE4C1',
    'orga1':'#00c40c98',
    'orga2':'#00c40c96',
    'orga3':'#00c40c94',
    'orga4':'#00c40c92',
    'orga5':'#00c40c90',
    'theme1':'#ffff0078',
    'theme2':'#ffff0076',
    'theme3':'#ffff0074',
    'theme4':'#ffff0072',
    'theme5':'#ffff0070',
    'theme6':'#ffff0068',
    'groupe1':'#ff000038',
    'groupe2':'#ff000036',
    'groupe3':'#ff000034',
    'groupe4':'#ff000032',
    'groupe5':'#ff000030',
    'groupe6':'#ff000028',
    "Infos":"#A8EF8E",
    'administratif':"#8CCB75",
    'evenement':"#ACEADB",
    "elevage":"#80D8C4",
    "maraichage":"#59998B",
    "arboriculture":"##B4E81A",
    "Commission":"#DFF994",
    "ppam":"#C9E182",
    }
    couleurs_projets = {
        'Part':"#d0e8da", 'AGO':"#dcc0de", 'Projlong':"#d1d0dc", 'Projcourt':"#ffc09f", 'Projponct':"#e4f9d4",
    }


    couleurs_lien ={'article':'#058265', 'atelier':'#fbd818', 'document':'#ffcc99', 'projet':'#365BEC','categorie':"#f47a3f", 'tags':"#d98cd9", "pad":"#666699"}


    ordre_tri_articles = {
                             "date du dernier commentaire":'-date_dernierMessage',
                             "date de création":'-date_creation',
                             "date de la dernière modification":'-date_modification',
                             "date associée à l'article":'-start_time',
                             "titre": 'titre' }
    ordre_tri_projets = {"date de création":'-date_creation',
                         #"date du dernier commentaire":'-date_dernierMessage',
                         "Type de projet":'categorie', "statut du projet":"statut",
                         'auteur':'auteur', 'titre':'titre'}
    logo_asso = {
        "public": "nom_public.webp",
        "pc": "nom_pc.png",
        "scic": "nom_scic.png",
        "fer": "nom_fer.png",
        "rtg": "nom_rtg.png",
        "viure": "nom_viure.webp",
        "citealt": "nom_citealt.webp",
        "bzz2022": "nom_bzz2022.webp",
        "jp": "nom_jp.webp",
        "conf66":"nom_conf66.png",
        "ssa":"nom_ssa.png"
    }

    type_marqueur = ('0','Vert (défaut)'), ('1','Bleu'), ('2','Rouge'), ('3','Jaune'),  ('4','Orange'),  ('5','Violet'), ('6','Or'), ('7','Noir'), ('8','Gris')

    LIENS_ARTICLES = (
        ("0", "Thème commun ou similaire"),
        ("1", "Collectif/projet commun ou similaire"),
        ("2", "L'article englobe/contient (choisir l'article qui est contenu)"),
        ("3", "L'article est inclu dans l'autre (choisir l'article qui le contient)"),
        ("4", "info mère (choisir l'article qui hérite)"),
        ("5", "info fille (choisir l'article qui lègue)"),
        ("6", "info soeur"),
    )

    LIENS_PROJET = (
        ("0", "Info sur le projet"),
        ("1", "Info en lien avec le projet"),
        ("2", "Budget"),
        ("3", "Organisation"),
        ("4", "Logistique"),
        ("5", "Partenaires"),
        ("6", "Atelier/rencontre"),
        ("6", "Autre"),
    )

    def get_couleur(categorie):
        try:
            return Choix.couleurs_annonces[categorie]
        except:
            return Choix.couleurs_annonces["Autre"]

    def get_logo(categorie):
        try:
            return Choix.type_annonce_citealt_groupes_logo[categorie]
        except:
            return ""

    def get_logo_nomgroupe(slug):
        return 'img/logos/'+ Choix.logo_asso[slug]
        #return 'img/logos/nom_'+slug+'.png'

    def get_logo_nomgroupe_html(slug, taille=18):
        try:
            return "<img src='/static/" + Choix.get_logo_nomgroupe(slug) + "' height ='"+str(taille)+"px' alt='"+ str(slug)+"'/>"
        except Exception as e:
            return slug

    def get_type_annonce_asso(asso):
        try:
            if asso =="jp":
                return Choix.type_annonce_jp_base + tuple([('jardin_' + str(i.id), "Jardin : " + i.titre) for i in Jardin.objects.all()])

            return Choix.type_annonce_asso[asso]
        except:
            return Choix.type_annonce

    def get_num_type_annonce_asso(asso):
        return

    def get_categorie_from_id(id_cat):
        try:
            return [x[1] for x in Choix.type_annonce if x[0] == id_cat][0]
        except:
            try:
                return [x[1] for x in Choix.type_annonce_jp_base if x[0] == id_cat][0]
            except:
                return "dossier inconnu"


    type_atelier = ('0','Permaculture'), ('1',"Bricolage"), ('2','Cuisine'), ('3','Bien-être'), ('4',"Musique"), ('6', 'Politique'), ('8', 'Culture'), ('7', 'Activité Pro'), ('9', 'Informatique'), ('5', 'Autre...'),
    couleurs_ateliers = {
        '2':'#4DC490', '1':'#C0EDA0', '3':'#00AA8B', '0':'#FCE79C',
        '5':"#d1ecdc",'3':"#fcf6bd", '4':"#d0f4de", '9':"#fff2a0", '7':"#ffac99",
        '10':"#ffc4c8", '8':"#bccacf", '6':"#87bfae", '11':"#bcb4b4"
    }
    statut_atelier = ('0', 'proposition'), ('1', "accepté, en cours d'organisation"), ('2', "accepté, s'est déroule correctement"), ('3', "a été annulé"),
    type_difficulte = ('0', 'facile'), ('1', "moyen"), ("2", "difficile")
    type_jauge = ('1', "1"), ("2", "2"), ("3", "3"), ("4", "4"), ("5", "5")
    type_budget = ('0', "0"), ('1', "1"), ("2", "2"), ("3", "3")
    type_temps = ('1', "1h"), ("2", "2h"), ("3", "3h"), ("4", "4h"), ("5", "6h"), ("6", "1 journée"),  ("7", "plusieurs jours"),  ("8", "plusieurs mois"),
    type_age = ('0', '3-6 ans'), ('1', "7-11 ans"), ("2", "12 ans et plus"), ("3", "3-11ans"), ("4", "Tout public")
    #type_atelier = ('0', 'Observation'), ('1', "Experience"), ("2", "Jardinage")

    def get_categorie(num):
        return Choix.type_atelier[int(num)][1]

    def get_difficulte(num):
        return Choix.type_difficulte[int(num)][1]

    def get_age(num):
        return Choix.type_atelier[int(num)][1]

    def get_typeAtelier(num):
        return Choix.type_atelier[int(num)][1]

    def get_couleur_cat(cat):
            return Choix.couleurs_ateliers[cat]

class Theme(models.Model):
    nom = models.CharField(max_length=20)

    def __str__(self):
        return self.nom


class ZoneGeo(models.Model):
    """Zone géographique """
    titre = models.CharField(max_length=250,)

    def __str__(self):
        return self.titre

class Article(models.Model):
    categorie = models.CharField(max_length=30,         
        choices= Choix.type_annonce,
        default='', verbose_name=_("Dossier"))
    titre = models.CharField(max_length=250,)
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=100)
    contenu = models.TextField(null=True)
    date_creation = models.DateTimeField(verbose_name=_("Date de parution"), default=timezone.now)
    date_modification = models.DateTimeField(verbose_name=_("Date de modification"), auto_now=False, null=True, )
    #estPublic = models.BooleanField(default=False, verbose_name=_('Public ou réservé aux membres permacat'))
    estModifiable = models.BooleanField(default=False, verbose_name=_("Modifiable par les autres"))
    estEpingle = models.BooleanField(default=False, verbose_name=_("Article épinglé"))
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)
    date_dernierMessage = models.DateTimeField(verbose_name=_("Date du dernier message"), auto_now=False, null=True, blank=True)
    dernierMessage = models.CharField(max_length=100, default=None, blank=True, null=True)
    estArchive = models.BooleanField(default=False, verbose_name=_("Archiver l'article"))
    start_time = models.DateField(verbose_name=_("Date de l'événement (pour apparaitre sur l'agenda, sinon vous pourrez toujours ajouter des évènements depuis l'article) "), null=True, blank=True, help_text="jj/mm/année")
    end_time = models.DateField(verbose_name=_("Date de fin (optionnel, pour affichage dans l'agenda"),  null=True,blank=True, help_text="jj/mm/année")
    tags = TaggableManager(verbose_name=_("Mots clés"),  help_text="Liste de mots-clés séparés par une virgule", blank=True)
    album = models.ForeignKey(Album, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Album photo associé"),  )
    partagesAsso = models.ManyToManyField(Asso, related_name="asso_partages", verbose_name=_("Partagé avec :"), blank=True)
    themes = models.ManyToManyField(Theme, related_name="themes", verbose_name=_("Thèmes :"), blank=True)
    zonegeo = models.ForeignKey(ZoneGeo, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Zone géographique"),  )

    class Meta:
        ordering = ('-date_creation', )
        
    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('blog:lireArticle', kwargs={'slug':self.slug})

    @property
    def get_absolute_url_site(self):
        return "https://www.perma.cat" + self.get_absolute_url()

    def sendMailArticle_newormodif(self, creation, forcerCreationMails):
        emails = []
        suiveurs = []
        url = self.get_absolute_url_site + "#ref-titre"
        if creation or forcerCreationMails:
            titre = "Nouvel article"
            message = "Un article a été posté dans le forum [" + str(self.asso.nom) + "] : '<a href='" + url + "'>" + self.titre + "</a>'"
            message_notif = "Un article a été posté dans le forum [" + str(self.asso.nom) + "] : "+ self.titre
            suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_' + str(self.asso.slug))
            suiveurs = [suiv for suiv in followers(suivi) if self.est_autorise(suiv) and self.auteur != suiv]
            emails = [suiv.email for suiv in suiveurs]
            for asso in self.partagesAsso.all():
                suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_' + str(asso.slug))
                suiveurs = [suiv for suiv in followers(suivi) if self.auteur != suiv and self.est_autorise(suiv)]
                emails += [suiv.email for suiv in suiveurs]
        else:
            temps_depuiscreation = timezone.now() - self.date_creation
            titre = "Article actualisé"
            message = "L'article [" + str( self.asso.nom) + "] '<a href='" + url + "'>" + self.titre + "</a>' a été modifié"
            message_notif = "L'article [" + str(self.asso.nom) + "] " + self.titre + " a été modifié"

            if temps_depuiscreation > timedelta(minutes=10):
                suiveurs = [suiv for suiv in followers(self) if self.est_autorise(suiv) and self.auteur != suiv]
                emails = [suiv.email for suiv in suiveurs]

        if emails:
            action.send(self, verb='emails', url=url, titre=titre, message=message, emails=emails)
            payload = {"head": titre, "body": message_notif,
                       "icon": static('android-chrome-256x256.png'), "url": url}
            for suiv in suiveurs:
                try:
                    send_user_notification(suiv, payload=payload, ttl=7200)
                except:
                    pass

    def save(self, sendMail=True, saveModif=True, forcerCreationMails=False, *args, **kwargs):
        ''' On save, update timestamps '''
        sendMail = sendMail and getattr(self, "sendMail", True)
        creation = False
        if not self.id:
            creation = True
            self.date_creation = timezone.now()
        else:
            if saveModif:
                self.date_modification = timezone.now()

        retour = super(Article, self).save(*args, **kwargs)

        if creation:
            discussion, created = Discussion.objects.get_or_create(article=self, titre="Discussion Générale")

        if sendMail:
            self.sendMailArticle_newormodif(creation, forcerCreationMails)

        return retour

    @property
    def get_couleur(self):
        try:
            return Choix.couleurs_annonces[self.categorie]
        except:
            return Choix.couleurs_annonces["Autre"]

    @property
    def get_partagesAsso(self):
        try:
            x = self.partagesAsso.filter(slug='public')
            if x:
                return x
            return self.partagesAsso.exclude(slug=self.asso.slug)
        except Exception as e:
            action.send(sender=self, verb='bug', description=str(e) + " ;" + str(self))
            return Asso.objects.none()

    @property
    def get_partagesAssotxt(self):
        return "\n".join([str(p) for p in self.get_partagesAsso])#"\n".join(

    @property
    def get_partagesAssoLogo(self):
        return html.format_html("{}", html.mark_safe(" ".join([Choix.get_logo_nomgroupe_html(p.slug, taille=17) for p in self.get_partagesAsso])))

    @property
    def get_logo_categorie(self):
        return Choix.get_logo(self.categorie)

    @property
    def get_categorie_display2(self):
        if self.asso.slug == 'jp':
            try:
                return Jardin.objects.get(id=str(self.categorie).split("jardin_")[1]).titre
            except:
                pass

        return self.get_categorie_display

    @property
    def get_logo_nomgroupe(self):
        return Choix.get_logo_nomgroupe(self.asso.slug)

    @property
    def get_logo_nomgroupe_html(self):
        return self.get_logo_nomgroupe_html_taille(20)

    def get_logo_nomgroupe_html_taille(self, taille=20):
        try:
            return Choix.get_logo_nomgroupe_html(self.asso.slug, taille)#"<img src='/static/" + self.get_logo_nomgroupe + "' height ='"+str(taille)+"px'/>"
        except Exception as e:
            action.send(self, verb='bug', description=str(e) + " ; " + self.titre)
            return None

    @property
    def get_logo_nomgroupespartages_html(self):
        return self.get_logo_nomgroupes_partages_html_taille(14)

    def get_logo_nomgroupes_partages_html_taille(self, taille=14):
        return [Choix.get_logo_nomgroupe_html(asso.slug, taille) for asso in self.get_partagesAsso]#"<img src='/static/" + self.get_logo_nomgroupe + "' height ='"+str(taille)+"px'/>"

    @property
    def getInfosHtml(self):
        nb_dates= Evenement.objects.filter(article=self).count() + 1 if self.start_time else 0
        nb_fichiers = Document.objects.filter(article=self).count()
        nb_docptg = DocumentPartage.objects.filter(article=self).count()
        nb_comm = Commentaire.objects.filter(article=self).count()
        nb_salon = Salon.objects.filter(article=self).count()
        html = ""
        if nb_dates:
            html += '&nbsp;<i class="fa fa-calendar">'+ str(nb_dates) +'</i>'
        if nb_fichiers:
            html += '&nbsp;<i class="fa fa-file">'+ str(nb_fichiers) +'</i>'
        if nb_docptg:
            html += '&nbsp;<i class="fa fa-link">'+ str(nb_docptg) +'</i>'
        if nb_comm:
            html += '&nbsp;<i class="fa fa-comment">'+ str(nb_comm) +'</i>'
        if nb_salon:
            html += '&nbsp;<i class="fa fa-users">'+ str(nb_salon) +'</i>'

        return mark_safe(html)

    def est_autorise(self, user):
        if user == self.auteur or self.partagesAsso.filter(slug="public").exists():
            return True
        elif self.asso.est_autorise(user):
            return True
        for asso in self.get_partagesAsso:
            if asso.est_autorise(user):
                return True
        return False

    def getLieux(self):
        return AdresseArticle.objects.filter(article=self)

    @property
    def derniereDate(self):
        derniere_date = self.date_modification if self.date_modification else self.date_creation
        if self.date_dernierMessage and self.date_dernierMessage > derniere_date:
            return self.date_dernierMessage
        else:
            return derniere_date

# class ModificationArticle(models.Model):
#     description = models.CharField(verbose_name=_("Explication de la modification"), max_length=500, null=True, blank=True)
#     article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name=_("article lié" ))
#     date_creation = models.DateTimeField(verbose_name=_("Date de la modif"), default=timezone.now)
#
#     def __str__(self):
#         return "(" + str(self.date_creation) + " : " +  self.article + ") "+ str(self.description)

class AssociationSalonArticle(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name=_("article lié" ))
    salon = models.ForeignKey(Salon, on_delete=models.CASCADE, verbose_name=_("Salon lié" ))

    class Meta:
        unique_together = ('article', 'salon',)

    def __str__(self):
        return str(self.salon) + " - "+ str(self.article)

class DocumentPartage(models.Model):
    nom = models.CharField(verbose_name=_("Nom du document (ou lien http)"), help_text="Minimum 6 lettres", max_length=100, null=True, blank=False, default="", validators=[MinLengthValidator(6)])
    article = models.ForeignKey(Article, on_delete=models.CASCADE, verbose_name=_("article lié" ))
    slug = models.SlugField(max_length=100)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "(" + str(self.nom) + ") "+ str(self.url)

    @property
    def url(self):
        if self.nom.startswith("http"):
            return self.nom
        return "https://semestriel.framapad.org/p/" + self.slug

    def get_url(self):
        return self.url

    def get_absolute_url(self):
        return self.url

class Evenement(models.Model):
    titre_even = models.CharField(verbose_name=_("Titre de l'événement (si laissé vide, ce sera le titre de l'article)"),
                             max_length=100, null=True, blank=True, default="")
    article = models.ForeignKey(Article, on_delete=models.CASCADE, help_text="L'evenement doit etre associé à un article" )
    start_time = models.DateField(verbose_name=_("Date"), null=False,blank=False, help_text="jj/mm/année" , default=timezone.now)
    end_time = models.DateField(verbose_name=_("Date de fin (optionnel pour un evenement sur plusieurs jours)"),  null=True,blank=True, help_text="jj/mm/année")
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE)

    def __str__(self):
        return "(" + str(self.titre) + ") "+ str(self.start_time) + ": " + str(self.article)

    def get_absolute_url(self):
        return self.article.get_absolute_url()

    @property
    def slug(self):
        return self.article.slug

    @property
    def titre(self):
        if not self.titre_even:
            return self.article.titre
        return self.titre_even

    @property
    def estPublic(self):
        return self.article.asso.slug == 'public'

    def est_autorise(self, user):
        return self.article.est_autorise(user)

    @property
    def get_logo_categorie(self):
        return self.article.get_logo_categorie

    @property
    def get_logo_nomgroupe(self):
        return self.article.get_logo_nomgroupe

    @property
    def get_logo_nomgroupe_html(self):
        return self.article.get_logo_nomgroupe_html_taille(taille=18)


class Discussion(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    titre = models.CharField(blank=False, max_length=32, verbose_name=_("Titre de la discussion"))
    slug = models.SlugField(max_length=32, default=uuid.uuid4)

    class Meta:
        unique_together = ('article', 'slug',)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return str(self.titre) + " (" + str(self.article) + ")"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.titre)
        super(Discussion, self).save(*args, **kwargs)

    @property
    def queArchives(self):
        """On teste si tous les messages sont anciens (pascetteannee).
        Si le dernier message (premier par ordre decroissant sur la date) est de cette année,
        alors 'queArchives' est False (il existe au moins un message qui n'est pas une archive)"""
        comms = self.commentaire_set.order_by('-date_creation')
        if comms:
            return comms[0].pascetteannee
        return False

class Commentaire(models.Model):
    auteur_comm = models.ForeignKey(Profil, on_delete=models.CASCADE)
    commentaire = models.TextField()
    #commentaire = models.TextField()

    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.__str__()

    @property
    def titre(self):
        return mark_safe(self.commentaire[:150])

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.auteur_comm) + ": " + str(self.article)

    def get_absolute_url(self):
        return self.article.get_absolute_url() + "#comm_" + str(self.id)

    @property
    def get_absolute_url_site(self):
        return self.article.get_absolute_url_site + "#idConversation"

    def get_absolute_url_discussion(self):
        return self.article.get_absolute_url() + "#idConversation"

    @property
    def get_edit_url(self):
        return reverse('blog:modifierCommentaireArticle',  kwargs={'id':self.id})

    @property
    def pascetteannee(self):
        #return self.date_creation.day + 10*self.date_creation.month != timezone.now().day + 10*timezone.now().month
        return self.date_creation.year != timezone.now().year

    def save(self, sendMail=False, *args, **kwargs):
        ''' On save, update timestamps '''
        emails = []
        suiveurs = []
        if not self.id:
            self.date_creation = timezone.now()
            suivi, created = Suivis.objects.get_or_create(nom_suivi='articles_' + str(self.article.asso.slug))
            titre = "Article commenté"
            message = str(self.auteur_comm.username) + " a commenté l'article [" + str(self.article.asso.nom) + "] '<a href='https://www.perma.cat" + str(self.get_absolute_url_discussion())+ "'>" + str(self.article.titre) + "</a>'"
            message_notif = str(self.auteur_comm.username) + " a commenté l'article [" + str(self.article.asso.nom) + "] : '" + str(self.article.titre) + "'"
            suiveurs = [suiv for suiv in followers(self.article) if
                      self.auteur_comm != suiv and self.article.est_autorise(suiv)]
            emails = [suiv.email for suiv in suiveurs]
            self.article.date_dernierMessage = timezone.now()
            self.article.save(sendMail)

        retour = super(Commentaire, self).save(*args, **kwargs)

        values = username_re.findall(self.commentaire)
        if values:
            for v in values:
                try:
                    if Profil.objects.filter(username__iexact=v).exists():
                        p = Profil.objects.get(username__iexact=v)
                        titre_mention = "Vous avez été mentionné dans un commentaire de l'article '" + self.article.titre  +"'"
                        msg_mention = str(self.auteur_comm.username) + " vous a mentionné <a href='https://www.perma.cat"+self.get_absolute_url_discussion()+"'>dans un commentaire</a> de l'article '" + self.article.titre +"'"
                        msg_mention_notif = " vous a mentionné dans un commentaire de l'article '" + self.article.titre +"'"
                        action.send(self, verb='emails', url=self.get_absolute_url(), titre=titre_mention, message=msg_mention,
                                    emails=[p.email, ])
                        action.send(self.auteur_comm, verb='mention_' + p.username, url=self.get_absolute_url(),
                                   description=msg_mention_notif, )

                        payload = {"head": titre_mention, "body": str(self.auteur_comm.username) + msg_mention_notif,
                                   "icon": static('android-chrome-256x256.png'), "url": self.get_absolute_url_site}
                        send_user_notification(p, payload=payload, ttl=7200)
                except:
                    pass

        if emails:
            action.send(self, verb='emails', url=self.get_absolute_url(), titre=titre, message=message, emails=emails)
            payload = {"head": titre, "body":message_notif,
                       "icon": static('android-chrome-256x256.png'), "url": self.get_absolute_url_site}
            for suiv in suiveurs:
                try:
                    send_user_notification(suiv, payload=payload, ttl=7200)
                except:
                    pass
        return retour

    def est_autorise(self, user):
        return self.projet.est_autorise(user)

class Projet(models.Model):
    categorie = models.CharField(max_length=10,
        choices=(Choix.type_projet),
        default='Part', verbose_name=_("categorie"))
    statut = models.CharField(max_length=5,
        choices=(Choix.statut_projet ),
        default='prop', verbose_name=_("statut"))
    titre = models.CharField(max_length=250)
    auteur = models.ForeignKey(Profil, on_delete=models.SET_NULL, null=True)
    slug = models.SlugField(max_length=100)
    contenu = models.TextField(null=True)
    date_creation = models.DateTimeField(verbose_name=_("Date de parution"), default=timezone.now)
    date_modification = models.DateTimeField(verbose_name=_("Date de modification"), default=timezone.now)
    #estPublic = models.BooleanField(default=False, verbose_name=_('Public (cochez) ou Interne (décochez) [réservé aux membres permacat]'))
    coresponsable = models.CharField(max_length=150, verbose_name=_("Référent du projet"), default='', null=True, blank=True)
    lien_vote = models.URLField(verbose_name=_('Lien vers le vote (balotilo.org)'), null=True, blank=True, )
    lien_document = models.URLField(verbose_name=_('Lien vers un document explicatif (en ligne)'), default='', null=True, blank=True)
    fichier_projet = models.FileField(upload_to='projets/%Y/%m/', blank=True, default=None, null=True)
    date_fichier = models.DateTimeField(auto_now=True, blank=True)

    date_dernierMessage = models.DateTimeField(verbose_name=_("Date de Modification"), auto_now=False, blank=True, null=True)
    dernierMessage = models.CharField(max_length=100, default="", blank=True, null=True)

    start_time = models.DateField(verbose_name=_("Date de début (optionnel, pour apparaitre dans l'agenda)"),  null=True,blank=True, help_text="jj/mm/année")
    end_time = models.DateField(verbose_name=_("Date de fin (optionnel, pour apparaitre dans l'agenda)"),  null=True,blank=True, help_text="jj/mm/année")

    estArchive = models.BooleanField(default=False, verbose_name=_("Archiver le projet"))
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)

    tags = TaggableManager(verbose_name=_("Mots clés"), help_text=_("Liste de mots-clés séparés par une virgule"), blank=True)

    class Meta:
        ordering = ('-date_creation', )

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('blog:lireProjet', kwargs={'slug':self.slug})

    @property
    def get_absolute_url_site(self):
        return "https://www.perma.cat" + self.get_absolute_url()

    def get_absolute_url_discussion(self):
        return self.get_absolute_url() + "#idConversation"

    def save(self, sendMail = True, *args, **kwargs):
        ''' On save, update timestamps '''
        emails = []
        if not self.id:
            self.date_creation = timezone.now()
            titre = "Nouveau Projet !"
            message = "Un nouveau projet a été proposé: ["+ self.asso.nom +"] '<a href='https://www.perma.cat" + self.get_absolute_url() + "'>" + str(self.titre) + "</a>'"
            suivi, created = Suivis.objects.get_or_create(nom_suivi='projets')
            emails = [suiv.email for suiv in followers(suivi) if self.auteur != suiv  and self.est_autorise(suiv)]

        else:
            if sendMail:
                titre = "Projet actualisé"
                message = "Le projet ["+ self.asso.nom +"] '<a href='https://www.perma.cat" + self.get_absolute_url() + "'>" + str(self.titre) + "</a>' a été modifié"
                emails = [suiv.email for suiv in followers(self) if
                          self.auteur != suiv and self.est_autorise(suiv)]

        retour = super(Projet, self).save(*args, **kwargs)
        if emails:
            action.send(self, verb='emails', url=self.get_absolute_url(), titre=titre, message=message, emails=emails)
        return retour

    @property
    def get_couleur(self):
        try:
            return Choix.couleurs_projets[str(self.categorie)]
        except:
            return Choix.couleurs_annonces["Autre"]

    def est_autorise(self, user):
        if user == self.auteur:
            return True
        return self.asso.est_autorise(user)

    @property
    def has_ficheprojet(self):
        return hasattr(self, "ficheprojet")

    @property
    def get_logo_nomgroupe_html(self, ):
        return self.asso.get_logo_nomgroupe_html_taille(taille=18)

class FicheProjet(models.Model):
    projet = models.OneToOneField(Projet, on_delete=models.CASCADE, primary_key=True,)
    date_creation = models.DateTimeField(verbose_name=_("Date de création"), auto_now_add=True)
    date_modification = models.DateTimeField(verbose_name=_("Date de modification"), auto_now=True)
    raison = models.TextField(null=True, blank=True, verbose_name=_("Raison d'Etre du projet"))
    pourquoi_contexte = models.TextField(null=True, blank=True, verbose_name=_("Pourquoi ? Le contexte"))
    pourquoi_motivation = models.TextField(null=True, blank=True, verbose_name=_("Pourquoi ? Les motivations"))
    pourquoi_objectifs = models.TextField(null=True, blank=True, verbose_name=_("Pourquoi ? Les objectifs"))
    pour_qui = models.TextField(null=True, blank=True, verbose_name=_("Pour qui ? Le public"))
    par_qui = models.TextField(null=True, blank=True, verbose_name=_("Par qui ? Les acteurs"))
    avec_qui = models.TextField(null=True, blank=True, verbose_name=_("Par qui ? Les partenaires"))
    ou = models.TextField(null=True, blank=True, verbose_name=_("Où ?"))
    quand = models.TextField(null=True, blank=True, verbose_name=_("Début ? La périodicité"))
    comment = models.TextField(null=True, blank=True, verbose_name=_("Comment ? La méthodologie"))
    combien = models.TextField(null=True, blank=True, verbose_name=_("Combien ? Le budget prévisionnel"))

    class Meta:
        ordering = ('-date_creation', )

    def __str__(self):
        return "Fiche du projet" + str(self.projet) + " créée le " + str(self.date_creation) + " "+ str(self.raison)

    def get_absolute_url(self):
        return reverse('blog:lireProjet', kwargs={'slug':self.projet.slug})


    def est_autorise(self, user):
        return self.projet.est_autorise(user)

    @property
    def titre(self):
        return self.projet.titre

class CommentaireProjet(models.Model):
    auteur_comm = models.ForeignKey(Profil, on_delete=models.CASCADE)
    commentaire = models.TextField(blank=True)
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.auteur_comm) + ": " + str(self.projet)

    def get_absolute_url(self):
        return self.projet.get_absolute_url()

    @property
    def get_absolute_url_site(self):
        return self.projet.get_absolute_url_site

    def get_absolute_url_discussion(self):
        return self.projet.get_absolute_url() + "#idConversation"

    @property
    def get_edit_url(self):
        return reverse('blog:modifierCommentaireProjet',  kwargs={'id':self.id})

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        emails = []
        if not self.id:
            titre = "[Permacat] Projet commenté"
            self.projet.date_dernierMessage = timezone.now()
            self.projet.save()
            message = self.auteur_comm.username + " a commenté le projet '<a href='https://www.perma.cat" + self.projet.get_absolute_url_discussion() + "'>" + self.projet.titre + "</a>'"
            emails = [suiv.email for suiv in followers(self.projet) if self.auteur_comm != suiv and self.est_autorise(suiv)]

        retour = super(CommentaireProjet, self).save(*args, **kwargs)

        values = username_re.findall(self.commentaire)
        if values:
            for v in values:
                try:
                    p = Profil.objects.get(username__iexact=v)
                    titre_mention = "Vous avez été mentionné dans un commentaire du projet '" + self.projet.titre  +"'"
                    msg_mention = str(self.auteur_comm.username) + " vous a mentionné <a href='https://www.perma.cat"+self.get_absolute_url_discussion()+"'>dans un commentaire</a> du projet '" + self.projet.titre +"'"
                    msg_mention_notif = " vous a mentionné dans un commentaire du projet '" + self.projet.titre +"'"
                    action.send(self, verb='emails', url=self.get_absolute_url(), titre=titre_mention,
                                message=msg_mention,
                                emails=[p.email, ])
                    action.send(self.auteur_comm, verb='mention_' + p.username, url=self.get_absolute_url(),
                                description=msg_mention_notif, )

                    payload = {"head": titre_mention, "body": str(self.auteur_comm.username) + msg_mention_notif,
                               "icon": static('android-chrome-256x256.png'), "url": self.get_absolute_url_site}
                    send_user_notification(p, payload=payload, ttl=7200)
                except Exception as e:
                    pass

        if emails:
            action.send(self, verb='emails', url=self.projet.get_absolute_url(), titre=titre, message=message, emails=emails)
        return retour


    def est_autorise(self, user):
        return self.projet.est_autorise(user)



class EvenementAcceuil(models.Model):
    titre_even = models.CharField(verbose_name=_("Titre de l'événement (si laissé vide, ce sera le titre de l'article)"),
                             max_length=100, null=True, blank=True, default="")
    article = models.ForeignKey(Article, on_delete=models.CASCADE,
                                help_text="L'evenement doit etre associé à un article existant (sinon créez un article avec une date)")
    date = models.DateTimeField(verbose_name=_("Date"), null=False, blank=False, help_text="jj/mm/année",
                                      default=timezone.now)

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.date) + ": " + str(self.article)

    def get_absolute_url(self):
        return self.article.get_absolute_url()

    @property
    def titre(self):
        if not self.titre_even:
            return self.article.titre
        return self.titre_even

    def est_autorise(self, user):
        return self.article.est_autorise(user)


class AdresseArticle(models.Model):
    titre = models.CharField(verbose_name=_("Nom du lieu"),
                             max_length=100, null=True, blank=True, default="")
    adresse = models.ForeignKey(Adresse, on_delete=models.CASCADE,)
    article = models.ForeignKey(Article, on_delete=models.CASCADE,
                                help_text="L'evenement doit etre associé à un article existant (sinon créez un article avec une date)")
    infos = models.TextField(verbose_name=_("Infos complémentaires"), null=True, blank=True)
    type_marqueur = models.CharField(max_length=5,
        choices= Choix.type_marqueur,
        default='0', verbose_name=_("type_marqueur"))

    def __str__(self):
        try:
            if self.titre:
                return str(self.titre) + " : " + str(self.adresse.get_adresse_str)
            else:
                return str(self.adresse.get_adresse_str)
        except:
            if self.adresse:
                return str(self.adresse.get_adresse_str)
            else:
                return "-"


    @property
    def get_edit_url(self):
        return reverse('blog:modifierAdresseArticle',  kwargs={'slug_article':self.article.slug, 'id_adresse':self.id})

    @property
    def get_delete_url(self):
        return reverse('blog:supprimerAdresseArticle',  kwargs={'slug_article':self.article.slug, 'id_adresse':self.id})

    @property
    def get_absolute_url(self):
        return reverse('blog:voirAdresseArticle',  kwargs={'id_adresseArticle': self.id})

    @property
    def get_url_map(self):
        return reverse('blog:voirAdresseArticle',  kwargs={'id_adresseArticle': self.id})

    @property
    def get_titre(self):
        if not self.titre:
            return ""
        return self.titre

    @property
    def get_marqueur(self):
        if self.type_marqueur:
            return Choix.nom_marqueur[self.type_marqueur]
        else:
            return 'greenIcon'

class TodoArticle(models.Model):
    titre = models.CharField(max_length=150)
    slug = models.SlugField(max_length=100)
    description = models.CharField(max_length=500, blank=True, null=True)
    date_creation = models.DateTimeField('Créé le', auto_now_add=True)
    date_modification = models.DateTimeField('Modifié le', auto_now=True)
    estFait = models.BooleanField(default=False)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, help_text="Article lié")

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return self.article.get_absolute_url()


class ArticleLiens(models.Model):
    date_creation = models.DateTimeField('Créé le', auto_now_add=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, help_text="Article de base")
    article_lie = models.ForeignKey(Article, on_delete=models.SET_NULL, blank=True, null=True, related_name="article_lie")
    type_lien = models.CharField("Type de lien", choices=Choix.LIENS_ARTICLES, default="0", max_length=2)

    def __str__(self):
        return str(self.article) + " " + str(self.type_lien) + " " + str(self.article_lie)

    def get_absolute_url(self):
        return self.article.get_absolute_url()

    def get_delete_url(self):
        return reverse("blog:supprimerArticleLiens", kwargs={"slug_article":self.article.slug, "pk":self.pk})

    def get_update_url(self):
        return reverse("blog:modifierArticleLiens", kwargs={"slug_article":self.article.slug, "pk":self.pk})

class ArticleLienProjet(models.Model):
    date_creation = models.DateTimeField('Créé le', auto_now_add=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, help_text="Article de base")
    projet_lie = models.ForeignKey(Projet, on_delete=models.SET_NULL, blank=True, null=True, related_name="projet_lie")
    type_lien = models.CharField("Type de lien", choices=Choix.LIENS_PROJET, default="0", max_length=2)

    def __str__(self):
        return str(self.article) + " " + str(self.type_lien) + " " + str(self.projet_lie)

    def get_absolute_url(self):
        return self.article.get_absolute_url()

    def get_delete_url(self):
        return reverse("blog:supprimerArticleLienProjet", kwargs={"slug_article":self.article.slug,"pk":self.pk})

    def get_update_url(self):
        return reverse("blog:modifierArticleLienProjet", kwargs={"slug_article":self.article.slug,"pk":self.pk})


class Article_recherche(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True,)

class Projet_recherche(models.Model):
    projet = models.ForeignKey(Projet, on_delete=models.CASCADE,
                               #help_text=mark_safe("<p style='color:teal'>Taper 2 lettres du titre du projet recherché'</p>")
                               )

