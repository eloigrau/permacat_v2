from django import template
import re

register = template.Library()

@register.filter(is_safe=True)
def nb_user_has_voted(proposal, user):
    return proposal.get_nb_user_has_voted(user)

@register.filter(is_safe=True)
def nb_user_clarifications_ok(proposal, user):
    return proposal.get_nb_user_clarifications_ok(user)

@register.filter(is_safe=True)
def nb_user_objections_ok(proposal, user):
    return proposal.get_nb_user_objections_ok(user)

@register.filter(is_safe=True)
def user_has_voted(proposal, user):
    return proposal.get_user_has_voted(user)

@register.filter(is_safe=True)
def user_clarifications_ok(proposal, user):
    return proposal.get_user_clarifications_ok(user)

@register.filter(is_safe=True)
def user_objections_ok(proposal, user):
    return proposal.get_user_objections_ok(user)

@register.filter(is_safe=True)
def bool_to_ouinon(test):
    return "Oui" if test else "Non"


@register.filter(is_safe=True)
def bool_to_avote(test):
    return "J'ai déjà voté" if test else "Je n'ai pas encore voté"