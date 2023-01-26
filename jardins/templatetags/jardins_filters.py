from django import template
from ..models import Choix
import re

register = template.Library()

@register.filter(is_safe=True)
def rechercher_nom_plante(value):
    return value.split(',')[0].replace(' ', '+')
