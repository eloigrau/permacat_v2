from django import forms
from .models import Adherent, Adhesion
from bourseLibre.models import Salon, InscritSalon
import django_filters
from django.db.models import Q
from .constantes import CHOIX_STATUTS, get_slug_salon,dict_ape
annees = ('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023')


class AdherentsCarteFilter(django_filters.FilterSet):
    descrip = django_filters.CharFilter(lookup_expr='icontains', method='get_descrip_filter', label="Chercher : ")

    statut = django_filters.ChoiceFilter(choices=CHOIX_STATUTS, label="Statut")

    production_ape = django_filters.ChoiceFilter(choices=[(p, dict_ape[p]) for p in Adherent.objects.all().values_list('production_ape', flat=True).distinct()], label="Production")

    bureau = django_filters.BooleanFilter(label="Membre du bureau", method='get_bureau_filter',)

    annees = django_filters.ChoiceFilter(choices=annees, method='get_annee_filter',label="Année", )

    def get_descrip_filter(self, queryset, field_name, value):
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

    def get_bureau_filter(self, queryset, field_name, value):
        membres = [p.pk for p in Salon.objects.get(slug=get_slug_salon()).getInscrits()]
        return queryset.filter(pk__in=membres)

    def get_production_ape_filter(self, queryset, field_name, value):
        return queryset.filter(production_ape=value)

    class Meta:
        model = Adherent
        fields = {
            'descrip': ['icontains', ],
            'statut': ['exact', ],
        }

