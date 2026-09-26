from django.db import models
from django.conf import settings


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


class ObjectionResponse(models.Model):
    objection = models.ForeignKey(Objection, on_delete=models.CASCADE, related_name='responses')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField(help_text="Piste de résolution ou argumentation")
    created_at = models.DateTimeField(auto_now_add=True)


class ProposalHistory(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE, related_name='history')
    content = models.TextField()
    reformulated_at = models.DateTimeField(auto_now_add=True)