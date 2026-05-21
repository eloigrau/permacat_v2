from bourseLibre.views import getNbNewNotifications
from bourseLibre.constantes import Choix as Choix_global
from blog.models import Projet
from ateliers.models import Atelier
from django.utils.timezone import now
from django.utils.functional import SimpleLazyObject

def navbar(request):
    def complicated_query():
        context_data = dict()
        try:
            if request.user.is_authenticated:
                context_data['favoris_list'] = request.user.getFavoris

            return context_data
        except:
            pass

    return SimpleLazyObject(complicated_query)
