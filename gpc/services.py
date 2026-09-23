from django.core.exceptions import ValidationError
from .models import Proposal, Objection


def submit_proposal(proposal: Proposal) -> None:
    if proposal.status != Proposal.Status.DRAFT:
        raise ValidationError("Seul un brouillon peut être soumis.")
    proposal.status = Proposal.Status.CLARIFICATION
    proposal.save()


def close_clarifications(proposal: Proposal) -> None:
    if proposal.status != Proposal.Status.CLARIFICATION:
        raise ValidationError("La proposition n'est pas en phase de clarification.")

    unanswered_count = proposal.clarifications.filter(answer__isnull=True).count()
    if unanswered_count > 0:
        raise ValidationError(
            f"Impossible de clôturer : l'auteur doit répondre aux {unanswered_count} question(s) en attente."
        )

    proposal.status = Proposal.Status.OBJECTION_ROUND
    proposal.save()


def close_objections(proposal: Proposal) -> None:
    if proposal.status != Proposal.Status.OBJECTION_ROUND:
        raise ValidationError("La proposition n'est pas en phase de recueil d'objections.")

    has_active_objections = proposal.objections.filter(
        is_valid_consent_objection=True,
        is_resolved=False
    ).exists()

    if not has_active_objections:
        proposal.status = Proposal.Status.ACCEPTED
    else:
        proposal.status = Proposal.Status.DELIBERATION

    proposal.save()


def resolve_objection(objection: Objection) -> None:
    """Marque une objection comme levée suite aux réponses/échanges."""
    objection.is_resolved = True
    objection.save()


def close_deliberation(proposal: Proposal) -> None:
    """
    Clôture la délibération.
    Si toutes les objections valides sont levées, la proposition est adoptée par consentement.
    Sinon, elle reste bloquée ou doit être reformulée.
    """
    if proposal.status != Proposal.Status.DELIBERATION:
        raise ValidationError("La proposition n'est pas en phase de délibération.")

    unresolved_objections = proposal.objections.filter(
        is_valid_consent_objection=True,
        is_resolved=False
    ).exists()

    if unresolved_objections:
        raise ValidationError("Certaines objections ne sont pas encore levées. Veuillez les résoudre ou reformuler la proposition.")

    proposal.status = Proposal.Status.ACCEPTED
    proposal.save()


def reformulate_proposal(proposal: Proposal, new_content: str) -> None:
    if proposal.status != Proposal.Status.DELIBERATION:
        raise ValidationError("La proposition doit être en délibération pour être reformulée.")

    if not new_content or not new_content.strip():
        raise ValidationError("Le texte de la reformulation ne peut pas être vide.")

    proposal.history.create(content=proposal.content)
    proposal.content = new_content.strip()
    proposal.status = Proposal.Status.OBJECTION_ROUND
    proposal.save()


def reject_proposal(proposal: Proposal) -> None:
    if proposal.status in [Proposal.Status.ACCEPTED, Proposal.Status.REJECTED]:
        raise ValidationError("Impossible de rejeter une proposition déjà finalisée.")

    proposal.status = Proposal.Status.REJECTED
    proposal.save()