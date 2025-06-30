from colour import Color
from bourseLibre.models import Lien_AssoSalon

dict_ape = {
    "-": "Non renseigné",
    "0111Z": "Culture de céréales (à l exception du riz), de légumineuses et de graines oléagineuses",
    "0114Z": "Culture de la canne à sucre",
    "0112Z": "Culture du riz",
    "0113Z": "Culture de légumes, de melons, de racines et de tubercules",
    "0115Z": "Culture du tabac",
    "0121Z": "Culture de la vigne",
    "0116Z": "Culture de plantes à fibres",
    "0119Z": "Autres cultures non permanentes",
    "0122Z": "Culture de fruits tropicaux et subtropicaux",
    "0123Z": "Culture d agrumes",
    "0124Z": "Culture de fruits à pépins et à noyau",
    "0125Z": "Culture d autres fruits d arbres ou d arbustes et de fruits à coque",
    "0126Z": "Culture de fruits oléagineux",
    "0127Z": "Culture de plantes à boissons",
    "0128Z": "Culture de plantes à épices, aromatiques, médicinales et pharmaceutiques",
    "0141Z": "Élevage de vaches laitières",
    "0142Z": "Élevage d autres bovins et de buffles",
    "0143Z": "Élevage de chevaux et d autres équidés",
    "0144Z": "Élevage de chameaux et d autres camélidés",
    "0145Z": "Élevage d ovins et de caprins",
    "0146Z": "Élevage de porcins",
    "0147Z": "Élevage de volailles",
    "0149Z": "Élevage d autres animaux",
    "0150Z": "Culture et élevage associés",
    "0161Z": "Activités de soutien aux cultures",
    "0162Z": "Activités de soutien à la production animale",
    "0163Z": "Traitement primaire des récoltes",
    "0164Z": "Traitement des semences",
    "0170Z": "Chasse, piégeage et services annexes",
    "0129Z": "Autres cultures permanentes",
    "0130Z": "Reproduction de plantes"
    }

list_ape = [(k, k+" : " + v) for k, v in dict_ape.items()]

CHOIX_STATUTS = ("0", "?"), ("1", "A titre principal"), ("2", "Cotisant Solidaire"), ("3", "Conjoint Collaborateur"), ("4", "Retraité.e"), ("5", "ATS"), ("6", "Porteur de projet")

CHOIX_MOYEN = ("VIR", "Virement"), ("CHQ", "Chèque"), ("ESP", "Espèce"), ("HA", "HelloAsso"), ("Autre", "Autre"),

def get_salon_particulier(asso_slug, slug_type="bureau"):
    #Pour retrouver le slug du bureau qui donne accès à... des fonctionnalités
    lien_bureau = Lien_AssoSalon.objects.filter(asso__slug=asso_slug, slug_type=slug_type)
    return lien_bureau.salon



CHOIX_CONTACTS = ("", "--------"), ("0", "Réponse OK"), ("1", "Pas de réponse"), ("2", "A répondu mais à rappeler"), ("3", "A répondu mais HOSTILE"), ("4", "Mauvais numéro"), ("6", "autre: "), ("5", "Je l'appellerai")

red = Color("#ffffcc")
NB_COLORS_RANGE = 5
RANGE_COLORS_PHONING = list(red.range_to(Color("#f9f06b"), NB_COLORS_RANGE))