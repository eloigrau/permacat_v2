from django.db import models
from blog.models import Article
from django.urls import reverse
from django.utils import timezone
import uuid
from bourseLibre.models import Profil, Suivis, Asso, username_re
from actstream.models import followers
from actstream import action
from webpush import send_user_notification
from django.templatetags.static import static
from bourseLibre.settings import DATE_INPUT_FORMAT

class Choix():
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

class Atelier(models.Model):
    categorie = models.CharField(max_length=30,
        choices=(Choix.type_atelier),
        default='0', verbose_name="categorie")
    statut = models.CharField(max_length=30,
        choices=(Choix.statut_atelier),
        default='proposition', verbose_name="Statut de l'atelier")
    titre = models.CharField(verbose_name="Titre de l'atelier",max_length=120)
    slug = models.SlugField(max_length=100, default=uuid.uuid4)
    description = models.TextField(null=True, blank=True)
    materiel = models.TextField(null=True, blank=True, verbose_name="Matériel/outils nécessaires")
    referent = models.CharField(max_length=120, null=True, blank=True,  verbose_name="Référent(e.s)")
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE, null=True)
    start_time = models.DateField(verbose_name="Date prévue (affichage dans l'agenda)", help_text="(jj/mm/an)", default=timezone.now, blank=True, null=True)
    heure_atelier = models.TimeField(verbose_name="Heure de début", help_text="Horaire de départ (hh:mm)", default="14:00", blank=True, null=True)
    heure_atelier_fin = models.TimeField(verbose_name="Heure de fin ", help_text="Horaire de fin (hh:mm)",
                                    default="17:00", blank=True, null=True)

    date_creation = models.DateTimeField(verbose_name="Date de parution", default=timezone.now)
    date_modification = models.DateTimeField(verbose_name="Date de modification", default=timezone.now)

    #date_dernierMessage = models.DateTimeField(verbose_name="Date du dernier message", auto_now=False, blank=True, null=True)
    #dernierMessage = models.CharField(max_length=100, default=None, blank=True, null=True, help_text="Heure prévue (hh:mm)")
    tarif_par_personne = models.CharField(max_length=100, default='gratuit', help_text="Tarif de l'atelier par personne", verbose_name="Tarif de l'atelier par personne", )
    asso = models.ForeignKey(Asso, on_delete=models.SET_NULL, null=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True, blank=True)

    estArchive = models.BooleanField(default=False, verbose_name="Archiver l'atelier")
    nbMaxInscriptions = models.IntegerField(verbose_name="Nombre maximum d'inscriptions", help_text="Nombre maximum de personnes inscrites", blank=True, null=True)

    class Meta:
        ordering = ('-date_creation', )
        
    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('ateliers:lireAtelier', kwargs={'slug':self.slug}) #+ "#idTitreAtelier"

    @property
    def get_absolute_url_site(self):
        return "https://www.perma.cat" + self.get_absolute_url()

    def save(self, sendMail=True, *args, **kwargs):
        ''' On save, update timestamps '''
        emails, suiveurs = [], []
        message_notif = ""
        if not self.id:
            self.date_creation = timezone.now()

            try:
                self.auteur
            except:
                self.auteur = Profil.objects.first()

            suivi, created = Suivis.objects.get_or_create(nom_suivi='ateliers')
            suiveurs = [suiv for suiv in followers(suivi) if self.est_autorise(suiv)]
            if sendMail:
                emails = [suiv.email for suiv in suiveurs ]
            else:
                emails = []
            titre = "Nouvel atelier proposé"
            if self.start_time:
                message = "L'atelier ["+ self.asso.nom +"]' <a href='https://www.perma.cat" + self.get_absolute_url() + "'>" + self.titre + "</a>' le " + self.start_time.strftime(DATE_INPUT_FORMAT) +" a été proposé"
                message_notif = "L'atelier ["+ self.asso.nom +"] '" + self.titre + "' le " + self.start_time.strftime(DATE_INPUT_FORMAT) +" a été proposé"
            else:
                message = "L'atelier ["+ self.asso.nom +"]' <a href='https://www.perma.cat" + self.get_absolute_url() + "'>" + self.titre + "</a>' a été proposé"
                message_notif = "L'atelier ["+ self.asso.nom +"] '" + self.titre + "' a été proposé"
        else:
            if sendMail:
                titre = "Atelier modifié"
                if self.start_time:
                    message = "L'atelier [" + self.asso.nom + "]' <a href='https://www.perma.cat" + self.get_absolute_url() + "'>" + self.titre + "</a>' le " + self.start_time.strftime(
                        DATE_INPUT_FORMAT) + " a été modifié"
                    message_notif = "L'atelier [" + self.asso.nom + "]' "+ self.titre + "' le " + self.start_time.strftime(
                        DATE_INPUT_FORMAT) + " a été modifié"
                else:
                    message = "L'atelier [" + self.asso.nom + "]' <a href='https://www.perma.cat" + self.get_absolute_url() + "'>" + self.titre + "</a>' a été modifié"
                    message_notif = "L'atelier [" + self.asso.nom + "]' " + self.titre + " a été modifié"

        ret = super(Atelier, self).save(*args, **kwargs)
        if emails:
            action.send(self, verb='emails', url=self.get_absolute_url_site, titre=titre, message=message, emails=emails)
            payload = {"head": titre, "body":message_notif,
                       "icon": static('android-chrome-256x256.png'), "url": self.get_absolute_url_site}
            for suiv in suiveurs:
                try:
                    send_user_notification(suiv, payload=payload, ttl=7200)
                except:
                    pass
        return ret


    @property
    def get_couleur(self):
        try:
            return Choix.couleurs_ateliers[self.categorie]
        except:
            return Choix.couleurs_ateliers['0']

    @property
    def get_inscrits(self):
        return [x[0] for x in InscriptionAtelier.objects.filter(atelier=self).values_list('user__username')]

    @property
    def get_couleur_cat(self, cat):
        try:
            return Choix.couleurs_ateliers[cat]
        except:
            return Choix.couleurs_ateliers['0']


    def est_autorise(self, user):
        if user == self.auteur:
            return True
        if self.asso.abreviation == "public":
            return True

        return getattr(user, "adherent_" + self.asso.abreviation)

    def est_complet(self):
        if not self.nbMaxInscriptions:
            return False
        return len(self.get_inscrits) >= self.nbMaxInscriptions

    @property
    def heure_fin_atelier(self,):
        if self.start_time and self.heure_atelier_fin:
            return self.heure_atelier_fin
        else:
            return None

    @property
    def get_logo_nomgroupe_html(self, ):
        return self.asso.get_logo_nomgroupe_html_taille(taille=18)



class CommentaireAtelier(models.Model):
    auteur_comm = models.ForeignKey(Profil, on_delete=models.CASCADE)
    commentaire = models.TextField()
    atelier = models.ForeignKey(Atelier, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.__str__()

    def __str__(self):
        return "(" + str(self.id) + ") "+ str(self.auteur_comm) + ": " + str(self.atelier)

    @property
    def get_edit_url(self):
        return reverse('ateliers:modifierCommentaireAtelier',  kwargs={'id':self.id})


    def get_absolute_url(self):
        return self.atelier.get_absolute_url()

    @property
    def get_absolute_url_site(self):
        return self.atelier.get_absolute_url_site

    def get_absolute_url_discussion(self):
        return self.atelier.get_absolute_url() + "#idConversation"

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        retour = super(CommentaireAtelier, self).save(*args, **kwargs)

        values = username_re.findall(self.commentaire)
        if values:
            for v in values:
                try:
                    p = Profil.objects.get(username__iexact=v)
                    titre_mention = "Vous avez été mentionné dans un commentaire de l'atelier '" + self.atelier.titre  +"'"
                    msg_mention = str(self.auteur_comm.username) + " vous a mentionné <a href='https://www.perma.cat"+self.get_absolute_url_discussion()+"'>dans un commentaire</a> de l'atelier '" + self.atelier.titre +"'"
                    msg_mention_notif = " vous a mentionné dans un commentaire de l'atelier '" + self.atelier.titre +"'"
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

        return retour

class InscriptionAtelier(models.Model):
    user = models.ForeignKey(Profil, on_delete=models.CASCADE)
    atelier = models.ForeignKey(Atelier, on_delete=models.CASCADE)
    date_inscription = models.DateTimeField(verbose_name="Date d'inscription", editable=False, auto_now_add=True)

    def __unicode__(self):
        return self.__str()

    def __str__(self):
        return "(" + str(self.id) + ") " + str(self.user) + " " + str(self.date_inscription) + " " + str(self.atelier)


