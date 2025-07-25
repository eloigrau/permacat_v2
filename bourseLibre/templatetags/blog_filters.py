from django import template
import re
from datetime import datetime

from django.utils.safestring import mark_safe

from blog.models import Choix
from hitcount.models import Hit
now = datetime.now()

register = template.Library()


def find_url(string):
    # findall() has been used
    # with valid conditions for urls in string
    #urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+] | [! * \(\),] | (?: %[0-9a-fA-F][0-9a-fA-F]))+', string)
    urls = re.findall('https?://[^\s]+', string)
    #urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', string)
    return urls

@register.filter(is_safe=True)
def url(value):
    url = find_url(value)
    newvalue = value
    for url_string in url:
        newurlstring = "<a href='" +url_string+"'" + " target='_blank'>"+url_string+"</a>"
        newvalue = newvalue.replace(url_string, newurlstring)
    return newvalue


@register.filter(is_safe=True)
def ordreTri(value):
    newvalue = value.replace('_', ' ').replace('-', '')
    return newvalue

@register.filter(is_safe=True)
def sansOrdreTri(value):
    newvalue = value.replace('ordreTri', 'prec')
    newvalue = newvalue.replace('page=', 'old=')
    return newvalue

@register.filter(is_safe=True)
def getCategorie_display(cat):
    return Choix.get_categorie_from_id(cat)
# @register.filter(is_safe=True)
# def dejavu(article, user):
#     newvalue = Hit.objects.filter(hitcount_content_object=article, user=user)
#     return newvalue.count


@register.filter(is_safe=True)
def lienVersUrl(lien):
    return mark_safe("<a href='" + lien + "'>" + lien +"</a>")


@register.filter(is_safe=True)
def date_annee(date):
    if date.year == now.year:
        return format(date, 'F j')
    return format(date, 'l d F Y')