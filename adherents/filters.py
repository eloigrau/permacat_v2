from django import forms
from .models import Adherent, Adhesion, Contact, ContactContact
from bourseLibre.models import Salon, InscritSalon
import django_filters
from django.db.models import Q, Count
from .constantes import CHOIX_STATUTS, get_salon_particulier, dict_ape
from datetime import date
from bourseLibre.settings import LOCALL

annees = [(str(an), str(an)) for an in range(2020, date.today().isocalendar()[0] + 1)] #('2020', '2020'), ('2021', '2021'), ('2022', '2022'), ('2023', '2023'), ('2023', '2023')


NBCONTACTS_CHOICES = (
    (0, 'Pas contacté'),
    (1, 'Un contact'),
    (2, 'Au moins une fois'),
    (3, "Plus d'une fois"),
)

STATUT_CHOICES = (
    (0, 'Tous'),
    (1, 'Votant Conf (ATP, ATS, CC)'),
    (2, 'Votant NonConf vérfié'),
    (3, 'Statut inconnu'),
    (4, 'Non votants (CotSol, porteur de projet'),
)


def get_choix_Production():
    return [(p, dict_ape[p] if p in dict_ape else str(p[:10]) + " (inconnu)") for p in
            Adherent.objects.filter(asso__slug="conf66").values_list('production_ape', flat=True).distinct() if p]


class AdherentsCarteFilter(django_filters.FilterSet):
    descrip = django_filters.CharFilter(lookup_expr='icontains', method='get_descrip_filter', label="Chercher : ", required=False)
    statut = django_filters.ChoiceFilter(choices=CHOIX_STATUTS, label="Statut")
    production_ape = django_filters.ChoiceFilter(choices=get_choix_Production(), label="Production", widget=forms.Select(attrs={'width':'100%;'}))
    bureau = django_filters.BooleanFilter(label="Membre du bureau", method='get_bureau_filter',)
    annees = django_filters.MultipleChoiceFilter(choices=annees, method='get_annee_filter', label="Année", widget=forms.CheckboxSelectMultiple(attrs={}))

    def __init__(self, asso_slug, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.asso_slug = asso_slug

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
        membres = [p.pk for p in get_salon_particulier(self.asso_slug).getInscritsEtInvites()]
        return queryset.filter(pk__in=membres)

    def get_production_ape_filter(self, queryset, field_name, value):
        return queryset.filter(production_ape=value)

    class Meta:
        model = Adherent
        fields = {
            'statut': ['exact', ],
        }
        widget = { }


class ContactCarteFilter(django_filters.FilterSet):
    descrip = django_filters.CharFilter(lookup_expr='icontains', method='get_descrip_filter', label="Chercher : ",
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '',
                                                             'tabindex': 1, 'autofocus': '1'}))
    istel = django_filters.BooleanFilter(label="avec un telephone", method='get_istel_filter', widget=forms.CheckboxInput(),)
    mescontacts = django_filters.BooleanFilter(label="Mes contacts", method='get_mescontacts_filter', widget=forms.CheckboxInput(),)
    dejacontacte = django_filters.ChoiceFilter(choices=NBCONTACTS_CHOICES, label="Déjà contacté", method='get_dejacontacte_filter', )
    statut = django_filters.ChoiceFilter(choices=STATUT_CHOICES, label="Statut", method='get_statut_filter', )
    production_ape = django_filters.ChoiceFilter(choices=get_choix_Production(), label="Production",  method='get_production_ape_filter',
                                                 widget=forms.Select(attrs={'width': '100%;'}))

    def get_statut_filter(self, queryset, field_name, value):
        if value == '0':
            return queryset
        elif value == '1':
            return queryset.filter(Q(adherent__statut="1") | Q(adherent__statut="3") | Q(adherent__statut="5"))
        elif value == '2':
            return queryset.filter(Q(commentaire__isnull=False) & Q(commentaire__icontains="Votant"))
        elif value == '3':
            return queryset.filter(Q(adherent__isnull=True )|Q(adherent__statut__isnull=True)|Q(adherent__statut="0"))
        elif value == '4':
            return queryset.filter(Q(adherent__statut="2") | Q(adherent__statut="4"))
        else:
            return queryset

    def get_production_ape_filter(self, queryset, field_name, value):
        return queryset.filter(adherent__production_ape=value)

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
                               Q(adresse__telephone__icontains=value)|
                               Q(nom__icontains=value)|
                               Q(prenom__icontains=value)|
                               Q(commentaire__icontains=value)
                               )

    def get_dejacontacte_filter(self, queryset, field_name, value):
        if value == '0':
            return queryset.annotate(num_b=Count('contactcontact')).filter(num_b=0)
        elif value == '1':
            return queryset.annotate(num_b=Count('contactcontact')).filter(num_b=1)
        if value == '2':
            return queryset.annotate(num_b=Count('contactcontact')).filter(num_b__gt=0)
        if value == '3':
            return queryset.annotate(num_b=Count('contactcontact')).filter(num_b__gt=1)
        else:
            return queryset

    def get_mescontacts_filter(self, queryset, field_name, value):
        if value:
            contacts = ContactContact.objects.filter(profil=self.user)
            return queryset.filter(contactcontact__in=contacts)
        else:
            return queryset

    class Meta:
        model = Contact
        fields = {
                  }


    def __init__(self, request, *args, **kwargs):
        self.user = request.user
        super(ContactCarteFilter, self).__init__(*args, **kwargs)