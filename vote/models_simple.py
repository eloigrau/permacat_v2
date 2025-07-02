import itertools

from django.db import models
from bourseLibre.models import Profil, Asso
from django.urls import reverse
from django.utils import timezone
from actstream.models import followers
from bourseLibre.models import Suivis
from actstream import action
from functools import cmp_to_key
from django.core.validators import MinLengthValidator
from django.utils.translation import gettext_lazy as _

class Choix():
    type_vote_bm =(('', '-----------'), (0, "Question binaire")),

    vote_ouinon = (('', '-----------'),
                     (0, ("Oui")),
                    (1, ("Non")),
                    (2, ("Ne se prononce pas")))

    couleurs_annonces = {
            '0':"#d1ecdc",
            'Coordination':"#D4CF7D",
            '1':"#E0E3AB",
            'Potager':"#AFE4C1",
            'PPAM':"#fff2a0",
            'Arbres':"#B2AFE4",
            'Administratif':"#d0f4de",
            '2':"#caf9b7",
            'Permaculture':"#ced2d3",
            'Documentation':"#349D9B",
            'Point':"#bccacf",
            'Autre':"#87bfae",
            'Ecovillage':"#cebacf",
            'Jardin':"#fffdcc",
            'Altermarché':"#daffb3",
            'aa':'#ddd0a8',

        }

    def get_couleur(categorie):
        try:
            return Choix.couleurs_annonces[categorie]
        except:
            return Choix.couleurs_annonces["Autre"]

def getStrFromChoix_majoritaire(type_choix, choix):
    return Choix.vote_majoritaire[type_choix][[y[0] for y in Choix.vote_majoritaire[type_choix]].index(choix)][1]
def getStrFromChoix_ouinon(choix):
    return Choix.vote_ouinon[[y[0] for y in Choix.vote_ouinon].index(choix)][1]

def sort_candidats(a, b):
    """
    Sort candidates by their majority gauge.

    a & b are the majority gauges of the candidates A & B
    (p_A, α_A, q_A) & (p_B, α_B, q_B)
    where
    - α is the majority grade;
    - p the percentage of votes strictly above α;
    - q the percentage of votes strictly below α.
    thus, A > B ⇔ α_A > α_B || (α_A == α_B && (p_A > max(q_A, p_B, q_B) || q_B > max(p_A, q_A, p_B)))
    (eq. 2, p.11 of the second article in README.md)
    """
    a, b = [float(x) for x in a.majority_gauge()], [float(x) for x in b.majority_gauge()]

    if a[1] > b[1]:
        return 1
    if b[1] > a[1]:
        return -1
    if a[0] > max(a[2], b[0], b[2]):
        return 1
    if b[0] > max(b[2], a[0], a[2]):
        return -1
    if b[2] > max(a[0], a[2], b[0]):
        return 1
    if a[2] > max(b[0], b[2], a[0]):
        return -1
    return 0


class Sondage_binaire(models.Model):
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='auteur_suffrage_simple')
    date_creation = models.DateTimeField(verbose_name=_("Date de parution"), default=timezone.now)
    article = models.ForeignKey("blog.Article", on_delete=models.CASCADE,
                                help_text="Article associé",
                                blank=True, null=True)
    question = models.CharField(max_length=150, verbose_name=_("Question (oui/non) soumise au vote ?"), validators=[MinLengthValidator(1)])

    def __str__(self):
        return str(self.question)

    def get_resultats(self):
        votes = self.votesimple_binaire_set.all()
        return Resultat_binaire(votes)

    def get_delete_url(self):
        return reverse("vote:supprimerSondageB", kwargs={"pk": self.pk})

    def get_absolute_url(self):
        return reverse("blog:lireArticle", kwargs={"slug": self.article.slug})

    def save(self,  *args, **kwargs):
        ''' On save, update timestamps '''
        emails = []
        if not self.id:
            self.date_creation = timezone.now()
        #    suivi, created = Suivis.objects.get_or_create(nom_suivi='suffrages')
        #    titre = "Nouveau vote"
        #    message = userProfile.username + " a lancé un nouveau vote ["+ str(self.asso.nom) +"]: '<a href='https://www.perma.cat"+ self.get_absolute_url() + "'>"+ self.titre + "</a>'"
        #    emails = [suiv.email for suiv in followers(suivi) if userProfile != suiv and self.est_autorise(suiv)]

        retour = super(Sondage_binaire, self).save(*args, **kwargs)
        #if emails:
        #    action.send(self, verb='emails', url=self.get_absolute_url(), titre=titre, message=message, emails=emails)
        return retour

class Resultat_binaire():

    def __init__(self, votes):
        self.votesOui = votes.filter(choix='0')
        self.votesNon = votes.filter(choix='1')
        self.votesNSPP = votes.filter(choix='2')
        self.nbOui = len(self.votesOui)
        self.nbNon = len(self.votesNon)
        self.nbNSPP = len(self.votesNSPP)
        self.nbTotal = self.nbOui + self.nbNon + self.nbNSPP
        self.nbOuiEtNon = self.nbOui + self.nbNon
        if self.nbTotal > 0:
            self.nbOui = (len(self.votesOui), str(round(len(self.votesOui) * 100 / self.nbTotal, 1)) + '%')
            self.nbNon = (len(self.votesNon), str(round(len(self.votesNon) * 100 / self.nbTotal, 1)) + '%')
            self.nbNSPP = (len(self.votesNSPP), str(round(len(self.votesNSPP) * 100 / self.nbTotal, 1)) + '%')
            if self.nbOui > self.nbNon:
                if not self.nbOuiEtNon:
                    self.resultat = 'Oui à ' + str(round(self.nbOui[0] * 100 / self.nbTotal, 1)) + ' %' + ' (100% des votes exprimés)'
                else:
                    self.resultat = 'Oui à ' + str(round(self.nbOui[0] * 100 / self.nbTotal, 1)) + ' %' + ' (' + str(round(self.nbOui[0] * 100.0/self.nbOuiEtNon)) + ' % des votes exprimés)'
            elif self.nbNon > self.nbOui:
                if self.nbOuiEtNon:
                    self.resultat = 'Non à ' + str(round(self.nbNon[0] * 100 / self.nbTotal, 1)) + ' % (100% des votes exprimés)'
                else:
                    self.resultat = 'Non à ' + str(round(self.nbNon[0] * 100 / self.nbTotal, 1)) + ' %' + str(round(self.nbNon[0] * 100.0/self.nbOuiEtNon)) + ' % des votes exprimés)'
            else:
                if self.nbOuiEtNon:
                    self.resultat = 'Ex aequo à ' + str(round(self.nbOui[0] * 100 / self.nbTotal, 1)) + ' %'
                else:
                    self.resultat = 'Ne se prononce pas'
        else:
            self.nbOui = (0, '0%')
            self.nbNon = (0, '0%')
            self.nbNSPP = (0, '0%')
            self.resultat = "pas de votants"



class VoteSimple_binaire(models.Model):
    auteur = models.ForeignKey(Profil, on_delete=models.CASCADE, related_name='auteur_vote_simple')
    question = models.ForeignKey(Sondage_binaire, on_delete=models.CASCADE)
    choix = models.IntegerField(choices=(Choix.vote_ouinon),
                                default=2, verbose_name=_("Choix du vote :"))
    date_creation = models.DateTimeField(verbose_name=_("Date de parution"), auto_now_add=True)

    class Meta:
        unique_together = ('auteur', 'question')

    def __str__(self):
        return getStrFromChoix_ouinon(self.choix)



#
# class Question_base(models.Model):
#     suffrage = models.ForeignKey(Suffrage, on_delete=models.CASCADE)
#
#     class Meta:
#         abstract = True
#
#     def get_absolute_url(self):
#         return reverse('vote:lireSuffrage', kwargs={'slug':self.suffrage.slug})
#
#     def __str__(self):
#         if getattr(self, "question"):
#             question = self.question
#
#             if self.question and self.question[-1] != "?":
#                 question += "?"
#
#             return question
#         return ""
#
#     def clean(self):
#
#         if getattr(self, "question") and self.question == '':
#             raise ValidationError('Empty error message')
#
# class Question_majoritaire_simple(Question_base):
#     question = models.CharField(max_length=150, verbose_name=_("Question (jugement majoritaire) soumise au vote :", validators=[MinLengthValidator(1)])
#     type_choix = models.CharField(max_length=30,
#         choices=(Choix.type_echelledevote), default='0', verbose_name=_("Type de choix de vote")
#
#     def __str__(self):
#         return str(self.question)
#
#     def get_resultats(self):
#         """Get the sorted list of all Candidates for this Election."""
#         res = sorted(self.proposition_m_simple_set.all(), key=cmp_to_key(sort_candidats))[::-1]
#         return [(str(x), x.majority_gauge_str(), x.percentage_per_choice(), x.nb_votes_absolu(), x.nb_points()) for x in res]
#
#     @property
#     def propositions(self):
#         prop = self.proposition_m_simple_set.all()
#         if prop:
#             return prop
#         else:
#             p = Proposition_m_simple(proposition="")
#             p.save(question_m=self)
#             return (p, )
#
#     def get_delete_url(self):
#         return reverse("vote:supprimerQuestionM", kwargs={"id_question":self.id, 'slug':self.suffrage.slug})
#
#     @property
#     def get_typeChoix_liste(self):
#         return [x[1] for x in Choix.vote_majoritaire[self.type_choix][1:]]
#
# class Proposition_m_simple(models.Model):
#     """An Election as Proposition_m as choices."""
#     question_m = models.ForeignKey(Question_majoritaire_simple, on_delete=models.CASCADE)
#     proposition = models.CharField(max_length=500, verbose_name=_("Proposition", null=False, blank=False, )
#
#     def __str__(self):
#         """Print the candidate."""
#         return str(self.proposition)
#
#     def save(self, question_m=None, *args, **kwargs):
#         ''' On save, update timestamps '''
#         self.question_m = question_m
#         return super(Proposition_m_simple, self).save(*args, **kwargs)
#
#
#     def get_absolute_url(self):
#         """Get the candidate's Election URL."""
#         return self.question_m.get_absolute_url()
#
#     def get_delete_url(self):
#         return reverse("vote:supprimerPropositionM", kwargs={"id_question":self.question_m.id, "id_proposition":self.id, 'slug':self.question_m.suffrage.slug})
#
#     def majority_gauge(self):
#         """Compute the majority gauge of this Candidate."""
#         count = self.reponsequestion_m_simple_set.count()
#         if not count:
#             return (0, 2, 0)
#         mention = self.reponsequestion_m_simple_set.order_by('choix')[count // 2].choix
#         if mention is None:
#             #print(self.reponsequestion_m_set.order_by('choix'))
#             mention = 2
#         return (self.reponsequestion_m_simple_set.filter(choix__gt=mention).count() / float(count), mention,
#                 self.reponsequestion_m_simple_set.filter(choix__lt=mention).count() / float(count))
#
#     def majority_gauge_str(self):
#         """Compute the majority gauge of this Candidate."""
#         majo = self.majority_gauge()
#         return [str(round(100.0*majo[2], 0)) + "%", getStrFromChoix_majoritaire(self.question_m.type_choix, majo[1]), str(round(100.0*majo[0])) + "%"]
#
#     def percentage_per_choice(self):
#         """Compute the majority gauge of this Candidate."""
#         count = self.reponsequestion_m_simple_set.count()
#         if not count:
#             return [(mention, 0, 0) for x, mention in Choix.vote_majoritaire[self.question_m.type_choix][1:]]
#         pourcentages = []
#         for num_mention, mention in Choix.vote_majoritaire[self.question_m.type_choix][1:]:
#             compte = self.reponsequestion_m_simple_set.filter(choix=num_mention).count()
#             pourcentages.append([mention, compte, int(100.0 * compte/count + 0.5)])
#         return pourcentages
#
#     def votes(self):
#         """Get the list of the votes for this Candidate."""
#         count = self.reponsequestion_m_simple_set.count()
#         if count:
#             return [self.reponsequestion_m_simple_set.filter(choix=i).count() * 100.0 / count for i in [x[0] for x in Choix.vote_majoritaire[self.question_m.type_choix][1:]]]
#         return [0] * (len(Choix.vote_majoritaire) - 1)
#
#     def nb_votes_absolu_par_mention(self):
#         """Get the list of the votes for this Candidate."""
#         if self.nb_votes_absolu():
#             return [self.reponsequestion_m_simple_set.filter(choix=i).count() for i in [x[0] for x in Choix.vote_majoritaire[self.question_m.type_choix][1:]]]
#         return [0] * (len(Choix.vote_majoritaire[self.question_m.type_choix]) - 1)
#
#     def nb_votes_absolu(self):
#         """Get the list of the votes for this Candidate."""
#         return self.reponsequestion_m_simple_set.count()
#
#     def nb_points(self):
#         """Get the list of the votes for this Candidate."""
#         if self.nb_votes_absolu():
#             # arrondi, de la somme des points calculés (mention pas du tout d'accord = 0 points, mention toutàafit d'accord = 4 points)
#             return round(sum([i*self.reponsequestion_m_simple_set.filter(choix=i).count() for i in
#                     [x[0] for x in Choix.vote_majoritaire[self.question_m.type_choix][1:]]])*100.0/(self.nb_votes_absolu() * 4), 1)
#
# class ReponseQuestion_m_simple(models.Model):
#     vote = models.ForeignKey(VoteSimple, on_delete=models.CASCADE, related_name='rep_question_m_simple')
#     proposition = models.ForeignKey(Proposition_m_simple, on_delete=models.CASCADE, default=None, null=True)
#     choix = models.IntegerField(
#         choices=Choix.vote_majoritaire['0'],
#         default=2, verbose_name=_("Choix du vote :")
#
#     def __str__(self):
#         return str(self.proposition) + ": " + getStrFromChoix_majoritaire(self.proposition.question_m_simple.type_choix, self.choix)
#
#     def str_sansproposition(self):
#         return getStrFromChoix_majoritaire(self.proposition.question_m.type_choix, self.choix)
#
#     def str_avecquestion(self):
#         return str(self.proposition.question_m), str(self)
