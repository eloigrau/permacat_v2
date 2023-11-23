from django import forms
from .models import Adherent
import django_filters
from django.db.models import Q

class AdherentsCarteFilter(django_filters.FilterSet):
    compet_descrip = django_filters.CharFilter(lookup_expr='icontains', method='get_competencedesritpion_filter', label="Chercher...")

    def get_competencedesritpion_filter(self, queryset, field_name, value):
        return queryset.filter(Q(email__icontains=value)|
                               Q(profil__username__icontains=value)|
                               Q(adresse__commune__icontains=value)|
                               Q(adresse__code_postal__icontains=value)|
                               Q(nom__icontains=value)|
                               Q(prenom__icontains=value)|
                               Q(statut__icontains=value))

    class Meta:
        model = Adherent
        fields = {
            'compet_descrip': ['icontains', ],
        }

