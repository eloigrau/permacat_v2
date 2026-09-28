from django.db import models
from django.conf import settings
from bourseLibre.models import Asso
from django.utils.translation import gettext_lazy as _


class Proposal(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Brouillon'
        CLARIFICATION = 'CLARIFICATION', 'Demandes de clarification'
        OBJECTION_ROUND = 'OBJECTION_ROUND', 'Recueil des objections'
        DELIBERATION = 'DELIBERATION', 'Délibération & Traitement'
        ACCEPTED = 'ACCEPTED', 'Adoptée (Consentement)'
        REJECTED = 'REJECTED', 'Refusée'

    title = models.CharField(max_length=255)
    context = models.TextField(help_text="Contexte et problème à résoudre")
    content = models.TextField(help_text="La proposition concrète / Formulation actuelle")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='proposals')
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    asso = models.ForeignKey(Asso, on_delete=models.CASCADE, verbose_name=_("Groupe"), null=False,)
    nbMinVote = models.IntegerField(verbose_name=_("Nombre minimum de participants (pour valider)"), help_text="Nombre minimum de personnes qui doivent participer pour valider ", blank=False, null=False, default="1")


    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class ClarificationQuestion(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='clarifications')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField(blank=True, null=True, help_text="Réponse fournie par l'auteur de la proposition")
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