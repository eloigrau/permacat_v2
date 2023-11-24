from django import forms
from .models import Adherent, Adhesion
import django_filters
from django.db.models import Q
from .constantes import CHOIX_STATUTS
annees = ('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023')

class AdherentsCarteFilter(django_filters.FilterSet):
    compet_descrip = django_filters.CharFilter(lookup_expr='icontains', method='get_competencedesritpion_filter', label="Chercher : ")

    statut = django_filters.ChoiceFilter(choices=CHOIX_STATUTS, label="Statut")

    annees = django_filters.ChoiceFilter(choices=annees, method='get_annee_filter',label="Année", )

    def get_competencedesritpion_filter(self, queryset, field_name, value):
        return queryset.filter(Q(email__icontains=value)|
                               Q(profil__username__icontains=value)|
                               Q(adresse__commune__icontains=value)|
                               Q(adresse__code_postal__icontains=value)|
                               Q(nom__icontains=value)|
                               Q(prenom__icontains=value)|
                               Q(statut__icontains=value))


    def get_statut_filter(self, queryset, field_name, value):
        return queryset.filter(statut=value[0])

    def get_annee_filter(self, queryset, field_name, value):
        cotisations = Adhesion.objects.filter(date_cotisation__year=value)
        return queryset.filter(adhesion__in=cotisations)

    class Meta:
        model = Adherent
        fields = {
            'compet_descrip': ['icontains', ],
            'statut': ['exact', ],
        }

