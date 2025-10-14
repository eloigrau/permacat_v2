from django import template
from django.forms import CheckboxInput
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.template.defaultfilters import stringfilter
from bourseLibre.constantes import Choix
from bourseLibre.models import Asso, username_re, Profil
from django_html_cleaner.cleaner import Cleaner
import random
import string
import re

register = template.Library()

class Constantes:
    typesAvecEntete = ['Select', " NumberInput", "DateInput", "DateTimeInputWidget", "SummernoteWidget",
                       "CheckboxSelectMultiple", "TextInput", 'Textarea', "ClearableFileInput","TagWidget",
                       "TimeInput"]
    #typesAvecEntete = ['Select', " NumberInput", "DateInput","DateTimeInputWidget", "SummernoteWidget", "CheckboxSelectMultiple", "TextInput" ]#'Textarea',
    width = 10
    dicoMois = {"January".center(width): "Janvier".center(width), "February".center(width): "Février".center(width),
                "March".center(width): "Mars".center(width), "April".center(width): "Avril".center(width),
                "May".center(width): "Mai".center(width), "June".center(width): "Juin".center(width),
                "July".center(width): "Juillet".center(width), "August".center(width): "Août".center(width),
                "September".center(width): "Septembre".center(width), "October".center(width): "Octobre".center(width),
                "November".center(width): "Novembre".center(width), "December".center(width): "Décembre".center(width),
            }

@register.filter(is_safe=True)
def is_numeric(value):
    return "{}".format(value).isdigit()


@register.filter(name='is_checkbox')
def is_checkbox(field):
  return field.field.widget.__class__.__name__ == CheckboxInput().__class__.__name__


@register.filter(name='field_type')
def field_type(field):
    return field.field.widget.__class__.__name__

@register.filter(name='field_entete')
def field_entete(field):
    type= str(field.field.widget.__class__.__name__)
    return (type in Constantes.typesAvecEntete)

@register.filter(name='nbsp')
def nbsp(value):
    return mark_safe("&nbsp;".join(value.split(' ')))


@register.filter(name='translate_month')
def translate_month(yearname):
    try:
        return Constantes.dicoMois[yearname]
    except:
        return yearname

@register.filter(name='translateOuiNon')
def translateOuiNon(truefalse):
    return "Oui" if truefalse else "Non"

@register.filter(name='translateFaitPasFait')
def translateFaitPasFait(truefalse):
    return "Fait" if truefalse else "Pas encore fait"


@register.filter(is_safe=True)
def ordreTriStr(value):
    if value == '-date_creation':
        return "Date de création"
    elif value =='-date_dernierMessage':
        return "Date du dernier message"
    elif value =='-date_modification':
        return "Date de modification"
    elif value =='categorie':
        return "Catégorie"
    elif value =='titre':
        return "Titre"
    else:
        return value


@register.filter(is_safe=True)
def couperTexte(value, nb):
    if len(value) > nb:
        return value[:nb-3] + "..."
    return value

@register.filter(is_safe=True)
def couperTexte2(value, nb):
    if len(value) > nb:
        return value[:nb-3] + " ..."
    return value

@register.filter(is_safe=True)
def couperTexte_avecbouton_150(value, id):
    nb = 150
    if len(value) > nb:
        #r = value[:nb-3] + "<button type='button' class ='btn btn-sm' onclick='toggle_visibility(\"graine_"+str(id)+"\");' data-toggle='tooltip' data-placement='bottom' title='Voir plus...' > </button><div id='graine_"+str(id)+"' style='display:none;'> "+value[nb-3:]+" </div>"
        r = "<button type='button' class ='btn btn-sm' onclick='toggle_visibility(\"graine_"+str(id)+"\");' data-toggle='tooltip' data-placement='bottom' title='Voir plus...' > <i class='fa fa-plus'> d'infos</i>  </button><div id='graine_"+str(id)+"' style='display:none;'> "+value+" </div>"
        return r
    return value

@register.filter(is_safe=True)
def adherent_asso(user, asso):
    return asso.is_membre(user)

@register.filter(is_safe=True)
def slug(txt):
    return slugify(txt)

@register.filter(is_safe=True)
def filtrerSuivis(nomSuivis):
    return Choix.nomSuivis[str(nomSuivis)]

@register.filter(is_safe=True)
def filtrerSuivisAgora(nomSuivis):
    try:
        if "agora" in str(nomSuivis):
            nomAsso = str(nomSuivis).split("_",1)[1]
            asso = Asso.objects.get(slug=nomAsso)
            return "Agora " + asso.nom
        else:
            nomSalon = str(nomSuivis).split("_",1)
            return "Salon " + nomSalon[1]
    except:
        return str(nomSuivis)


@register.filter(is_safe=True)
def filtrerSuivisForum(nomSuivis):
    try:
        nomAsso = str(nomSuivis).split("_",1)[1]
        asso = Asso.objects.get(slug=nomAsso)
        return "Articles " + asso.nom
    except:
        return str(nomSuivis)

@register.filter(is_safe=True)
def filtrerNotifSalon(nomSuivis):
    #return nomSuivis
    return str(nomSuivis).split(" (>")[0]

@register.filter(is_safe=True)
def distance(user1, user2):
    dist = None
    try:
        dist = user1.adresse.getDistance(user2.adresse)
    except:
        pass
    if dist == 0:
        return "-"
    elif dist == None:
        return "-"

    if dist < 1:
        return "1"

    return str(int(dist + 0.5))

@register.filter
def get_item_dict(dictionary, key):
    return dictionary.get(key)

@register.simple_tag
def random_name(longueur=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(longueur))

@register.filter
def raccourcirTempsStr(date):
    new = date.replace("heures","h")
    new = new.replace("heure","h")
    new = new.replace("minutes","mn")
    new = new.replace("minute","mn")
    splitted = new.split(", ")
    if splitted:
        return splitted[0]
    return new


def testeEtRemplaceMentionProfil(test):
    if Profil.objects.filter(username__iexact=test).exists():
        return '<a href="/accounts/profil/'+ test + '/"> '+test +'</a>'
    return test

@register.filter(name='usermention', is_safe=True)
@stringfilter
def usermention(value):
    profils = [v for v in username_re.findall(value) if Profil.objects.filter(username__iexact=v).exists()]
    for p in profils:
        value = value.replace('@' + p,  '<a href="/accounts/profil/'+ p + '/">@'+ p +'</a>')
    #value = re.sub(username_re, testeEtRemplaceMentionProfil, value)
    #value = re.sub(username_re, r'<a href="/accounts/profil/\1/"> @\1</a>', value)
    return value




"""
The tag generates a parameter string in form '?param1=val1&param2=val2'.
The parameter list is generated by taking all parameters from current
request.GET and optionally overriding them by providing parameters to the tag.

This is a cleaned up version of http://djangosnippets.org/snippets/2105/. It
solves a couple of issues, namely:
 * parameters are optional
 * parameters can have values from request, e.g. request.GET.foo
 * native parsing methods are used for better compatibility and readability
 * shorter tag name

Usage: place this code in your appdir/templatetags/add_get_parameter.py
In template:
{% load add_get_parameter %}
<a href="{% add_get param1='const' param2=variable_in_context %}">
Link with modified params
</a>

It's required that you have 'django.core.context_processors.request' in
TEMPLATE_CONTEXT_PROCESSORS

Original version's URL: http://django.mar.lt/2010/07/add-get-parameter-tag.html
"""


from django.template import Node, Variable
class AddGetParameter(Node):
    def __init__(self, values):
        self.values = values

    def render(self, context):
        req = Variable('request', context)
        params = req.GET.copy()
        for key, value in self.values.items():
            params[key] = value.resolve(context)
        return '?%s' % params.urlencode()


@register.tag
def add_get(parser, token):
    pairs = token.split_contents()[1:]
    values = {}
    for pair in pairs:
        s = pair.split('=', 1)
        values[s[0]] = parser.compile_filter(s[1])
    return AddGetParameter(values)


@register.filter(is_safe=True)
def sansMois(value):
    return re.sub('(mois=)(.*)(&)', '', value)
    #return value.replace('mois=', 'mois_old=')

@register.filter(is_safe=True)
def sansAsso(value):
    return re.sub('(asso=)(.*)(&)', '', value)


@register.filter(is_safe=True)
def cacherUser(value):
    nb = len(value)
    return value[:3] + "".join(['*' for i in range(nb-3)])


@register.filter(is_safe=True)
def filtrer_media_url(url):
    return url


@register.filter(is_safe=True)
def htmlClean(html):
    c = Cleaner()
    return c.clean(html)


@register.filter(is_safe=True)
def phonenumber(value):
    try:
        if len(value)<14:
            if value.startswith("+33"):
                phone = '%s %s %s %s %s' %(value[0:4],value[4:6],value[6:8],value[8:10],value[10:])
            else:
                phone = '%s %s %s %s %s' %(value[0:2],value[2:4],value[4:6],value[6:8],value[8:])
        else:
            phone = value
    except:
        return value
    return phone

@register.filter(is_safe=True)
def escapeETUrl(url):
    return url.replace('&', "%26")

@register.filter(is_safe=True)
def getLogoGroupeFromSlug(slug):
    return mark_safe(Asso.objects.get(slug=slug).get_logo_nomgroupe_html)

@register.filter(is_safe=True)
def getNomGroupeFromSlug(slug):
    return mark_safe(Asso.objects.get(slug=slug).nom)


@register.filter(is_safe=True)
def estMembreAsso(slug, user):
    return Asso.objects.get(slug=slug).est_autorise(user)

@register.filter(is_safe=True)
def is_adhesions(slug):
    return Asso.objects.get(slug=slug).is_adhesions

@register.filter(is_safe=True)
def is_defraiement(slug):
    return Asso.objects.get(slug=slug).is_defraiement

@register.filter(is_safe=True)
def is_listeContacts(slug):
    return Asso.objects.get(slug=slug).is_listeContacts

@register.filter(is_safe=True)
def is_listeDiffusion(slug):
    return Asso.objects.get(slug=slug).is_listeDiffusion