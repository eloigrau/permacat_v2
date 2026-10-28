from django import template
import re

register = template.Library()

@register.filter(is_safe=True)
def nb_has_voted(proposal):
    return proposal.get_nb_has_voted()

@register.filter(is_safe=True)
def nb_clarifications_ok(proposal):
    return proposal.get_nb_clarifications_ok()

@register.filter(is_safe=True)
def nb_objections_ok(proposal):
    return proposal.get_nb_objections_ok()

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
    return "J'ai voté" if test else "Je n'ai pas encore voté"