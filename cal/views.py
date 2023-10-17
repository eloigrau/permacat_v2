# cal/views.py

from datetime import datetime,  timedelta
from django.utils.safestring import mark_safe

from django.contrib.auth.decorators import login_required
from .utils import Calendar
from django.shortcuts import render
from calendar import monthrange
from bourseLibre.models import Suivis, Asso
from hitcount.models import HitCount
from hitcount.views import HitCountMixin
from bourseLibre.constantes import Choix as Choix_global



def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return datetime(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'mois=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'mois=' + str(next_month.year) + '-' + str(next_month.month)
    return month

@login_required
def agenda(request):
    # use today's date for the calendar
    if not 'mois' in request.GET:
        d = get_date(request.GET.get('day', None))
    else:
        d = get_date(request.GET.get('mois', None))

    # Instantiate our calendar class with today's year and date
    cal = Calendar(d.year, d.month)

    asso_list = Choix_global.abreviationsNomsAssoEtPublic  # [(x.nom, x.abreviation) for x in Asso.objects.all().order_by("id") if self.request.user.est_autorise(x.abreviation)]

    if 'asso' in request.GET:
        asso_abreviation = request.GET['asso']
        asso_courante = Asso.objects.get(abreviation=asso_abreviation).nom
    else:
        asso_courante = None
        asso_abreviation = None

    # Call the formatmonth method, which returns our calendar as a table
    html_cal = mark_safe(cal.formatmonth(request, withyear=True, asso_abreviation=asso_abreviation))


    suivi, created = Suivis.objects.get_or_create(nom_suivi='visite_agenda')
    hit_count = HitCount.objects.get_for_object(suivi)
    hit_count_response = HitCountMixin.hit_count(request, hit_count)
    return render(request, 'calendrier.html', {'calendar': html_cal, 'annee': d.year, 'mois': cal.formatmonthname(d.year, d.month, withyear=False, width=10),
                                               'prev_month':prev_month(d), 'next_month':next_month(d),
                                               'asso_list':asso_list,
                                               'asso_courante':asso_courante,
                                               'asso_courante_abreviation':asso_abreviation
                                               })
