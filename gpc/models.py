from django.db import models
from django.conf import settings
from bourseLibre.models import Asso, Profil
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


class Proposal(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Brouillon'
        CLARIFICATION = 'CLARIFICATION', 'Demande de clarification'
        OBJECTION_ROUND = 'OBJECTION_ROUND', 'Recueil des objections'
        REFORMULATION = 'REFORMULATION', 'Reformulation'
        OBJECTION_RESPONSE = 'OBJECTION_RESPONSE', 'warning'
        DELIBERATION = 'DELIBERATION', 'Délibération & Traitement'
        ACCEPTED = 'ACCEPTED', 'Adoptée (Consentement)'
        REJECTED = 'REJECTED', 'Refusée'


    title = models.CharField(max_length=255)
    context = models.TextField(verbose_name="Contexte et problème à résoudre", help_text="De quoi parle-t-on ? Liens utiles ?")
    content = models.TextField(verbose_name="La proposition concrète / Formulation actuelle", help_text="Une ou deux phrases pour prendre une décision claire")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='proposals')
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    asso = models.ForeignKey(Asso, on_delete=models.CASCADE, verbose_name=_("Groupe"), null=False,)
    nbMinVote = models.IntegerField(verbose_name=_("Nombre minimum de participants (pour valider)"), help_text="Nombre minimum de personnes qui doivent participer pour valider ", blank=False, null=False, default="1")


    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def get_absolute_url(self):
        return reverse('gpc:proposal_detail', kwargs={'pk':self.pk})

    def est_autorise(self, user):
        if user == self.author:
            return True
        elif self.asso.est_autorise(user):
            return True
        return False

    def get_user_has_voted(self, user):
        return self.resolution_votes.filter(voter=user).exists()

    def get_nb_user_has_voted(self, user):
        return self.resolution_votes.filter(voter=user).count()

    def get_user_clarifications_ok(self, user):
        return self.clarifications_ok.filter(author=user).exists()

    def get_nb_user_clarifications_ok(self, user):
        return self.clarifications_ok.filter(author=user).count()

    def get_user_objections_ok(self, user):
        return self.objections_ok.filter(author=user).exists()

    def get_nb_user_objections_ok(self, user):
        return self.objections_ok.filter(author=user).count()


class ClarificationQuestion(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='clarifications')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True, help_text="Réponse fournie par l'auteur de la proposition")
    created_at = models.DateTimeField(auto_now_add=True)

class ClarificationVoteOK(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='clarifications_ok')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class ObjectionVoteOK(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='objections_ok')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Objection(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='objections')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    description = models.TextField(help_text="Expliquer le risque majeur ou l'impact négatif")
    is_valid_consent_objection = models.BooleanField(default=True)
    is_resolved = models.BooleanField(default=False, help_text="Marqué comme vraie si l'objection a été levée")
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def positive_votes_count(self):
        """Nombre de votes distincts favorables à la levée."""
        return self.resolution_votes.filter(approve_resolution=True).values('voter').distinct().count()

    @property
    def votes_needed_to_resolve(self):
        """Nombre de votes positifs manquants pour atteindre le seuil de 3."""
        return max(0, 3 - self.positive_votes_count)

class ObjectionResolutionVote(models.Model):
    """Vote d'un membre pour accepter/valider la levée d'une objection."""
    objection = models.ForeignKey(Objection, on_delete=models.CASCADE, related_name='resolution_votes')
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    approve_resolution = models.BooleanField(default=True, help_text="Vrai = Pour lever l'objection, Faux = Contre")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('objection', 'voter')

class ObjectionResponse(models.Model):
    objection = models.ForeignKey(Objection, on_delete=models.CASCADE, related_name='responses')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(help_text="Piste de résolution ou argumentation")
    created_at = models.DateTimeField(auto_now_add=True)


class ProposalHistory(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='history')
    content = models.TextField()
    reformulated_at = models.DateTimeField(auto_now_add=True)


class PhaseVote(models.Model):
    proposal = models.ForeignKey(
        Proposal,
        on_delete=models.CASCADE,
        related_name='resolution_votes'
    )
    voter = models.ForeignKey(Profil, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('proposal', 'voter')