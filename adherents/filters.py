from django import forms
from .models import Adherent, Adhesion, Contact
from bourseLibre.models import Salon, InscritSalon
import django_filters
from django.db.models import Q
from .constantes import CHOIX_STATUTS, get_slug_salon,dict_ape
from datetime import date

annees = [(str(an), str(an)) for an in range(2020, date.today().isocalendar()[0] + 1)] #('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2023', '2023')


def get_choix_Production():
    return [(p, dict_ape[p] if p in dict_ape else p) for p in Adherent.objects.all().values_list('production_ape', flat=True).distinct() ]


class AdherentsCarteFilter(django_filters.FilterSet):
    descrip = django_filters.CharFilter(lookup_expr='icontains', method='get_descrip_filter', label="Chercher : ", required=False)

    statut = django_filters.ChoiceFilter(choices=CHOIX_STATUTS, label="Statut")

    production_ape = django_filters.ChoiceFilter(choices=get_choix_Production(), label="Production")

    bureau = django_filters.BooleanFilter(label="Membre du bureau", method='get_bureau_filter',)

    annees = django_filters.MultipleChoiceFilter(choices=annees, method='get_annee_filter',label="Année")

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
        cotisations = Adhesion.objects.filter(date_cotisation__year__in=value)
        return queryset.filter(adhesion__in=cotisations).distinct()

    def get_bureau_filter(self, queryset, field_name, value):
        membres = [p.pk for p in Salon.objects.get(slug=get_slug_salon()).getInscritsEtInvites()]
        return queryset.filter(pk__in=membres)

    def get_production_ape_filter(self, queryset, field_name, value):
        return queryset.filter(production_ape=value)

    class Meta:
        model = Adherent
        fields = {
            'statut': ['exact', ],
        }


class ContactCarteFilter(django_filters.FilterSet):
    descrip = django_filters.CharFilter(lookup_expr='icontains', method='get_descrip_filter', label="Chercher : ",
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '',
                                                             'tabindex': 1, 'autofocus': '1'}))
    isatp = django_filters.BooleanFilter(label="ATP (ou statut inconnu)", method='get_isatp_filter', widget=forms.CheckboxInput(),)
    istel = django_filters.BooleanFilter(label="avec un telephone", method='get_istel_filter', widget=forms.CheckboxInput(),)

    def get_isatp_filter(self, queryset, field_name, value):
        if value:
            return queryset.filter(Q(adherent__isnull=True )|Q(adherent__statut="1" )|Q(adherent__statut="3")|Q(adherent__statut="5")|Q(adherent__statut__isnull=True))
        else:
            return queryset

    def get_istel_filter(self, queryset, field_name, value):
        if value:
            return queryset.exclude(adresse__telephone__startswith=" ").exclude(adresse__telephone__iexact="")
        else:
            return queryset

    def get_descrip_filter(self, queryset, field_name, value):
        return queryset.filter(Q(email__icontains=value)|
                               Q(adresse__rue__icontains=value)|
                               Q(adresse__commune__icontains=value)|
                               Q(adresse__code_postal__icontains=value)|
                               Q(nom__icontains=value)|
                               Q(prenom__icontains=value)
                               )


    class Meta:
        model = Contact
        fields = {
                  }
