# from .models import Jardin, Grainotheque, Choix
# #import django_filters
# from django.db.models import Q
#
# class JardinCarteFilter(django_filters.FilterSet):
#     compet_descrip = django_filters.CharFilter(lookup_expr='icontains', method='get_jardin_filter', label="Mot dans le titre ou  la description")
#     categorie = django_filters.MultipleChoiceFilter(choices=Choix.type_jardin, method='get_jardin_type', )
#
#     def get_jardin_filter(self, queryset, field_name, value):
#         return queryset.filter(Q(auteur__email__icontains=value)|
#                                Q(auteur__username__icontains=value)|
#                                Q(referent__username__icontains=value)|
#                                Q(adresse__commune__icontains=value)|
#                                Q(adresse__code_postal__icontains=value)|
#                                Q(description__icontains=value)|
#                                Q(titre__icontains=value))
#
#     def get_jardin_type(self, queryset, field_name, choices):
#         q_objects = Q()  # Create an empty Q object to start with
#         for t in choices:
#             q_objects |= Q(categorie__contains=t)
#         return queryset.filter(q_objects)
#
#     class Meta:
#         model = Jardin
#         fields = {
#             #'compet_descrip': ['icontains', ],
#             'categorie': ['icontains', ]
#         }
#
#
# class GrainoCarteFilter(django_filters.FilterSet):
#     #compet_descrip = django_filters.CharFilter(lookup_expr='icontains', method='get_graino_filter', label="Mot dans le titre ou la description")
#
#     def get_graino_filter(self, queryset, field_name, value):
#         return queryset.filter(Q(email__icontains=value)|
#                                Q(auteur__username__icontains=value)|
#                                Q(referent__username__icontains=value)|
#                                Q(adresse__commune__icontains=value)|
#                                Q(adresse__code_postal__icontains=value)|
#                                Q(description__icontains=value)|
#                                Q(titre__icontains=value))
#
#     class Meta:
#         model = Grainotheque
#         fields = {
#             #'compet_descrip': ['icontains', ]
#         }
