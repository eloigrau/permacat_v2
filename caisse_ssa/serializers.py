from rest_framework import serializers
from bourseLibre.models import Profil
from .models import MembreSSA, LieuDeVente, Cotisation, Transaction


class MembreSSASerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    email = serializers.EmailField(source='user.email', required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    solde_june = serializers.SerializerMethodField()
    solde_euros = serializers.SerializerMethodField()

    class Meta:
        model = MembreSSA
        fields = [
            'id', 'username', 'email', 'password',
            'role', 'cotisation_mensuelle_engagee',
            'est_allocataire', 'est_cocreateur_du',
            'solde_june', 'solde_euros'
        ]

    def get_solde_june(self, obj):
        return str(obj.get_compte('JUNE').solde)

    def get_solde_euros(self, obj):
        return str(obj.get_compte('EUROS').solde)

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = validated_data.pop('password', None)
        profil, created = Profil.objects.get_or_create(
            username=user_data['username'],
            defaults={'email': user_data.get('email', '')}
        )
        if created and password:
            profil.set_password(password)
            profil.save()

        membre_ssa, _ = MembreSSA.objects.get_or_create(
            user=profil,
            defaults=validated_data
        )
        membre_ssa.get_compte('JUNE')
        membre_ssa.get_compte('EUROS')
        return membre_ssa


class LieuDeVenteSerializer(serializers.ModelSerializer):
    solde_june = serializers.SerializerMethodField()
    solde_euros = serializers.SerializerMethodField()

    class Meta:
        model = LieuDeVente
        fields = [
            'id', 'nom', 'type_lieu', 'gestionnaire', 'adresse', 'siret',
            'code_paiement', 'est_conventionne', 'date_conventionnement',
            'solde_june', 'solde_euros'
        ]
        read_only_fields = ['code_paiement']

    def get_solde_june(self, obj):
        return str(obj.get_compte('JUNE').solde)

    def get_solde_euros(self, obj):
        return str(obj.get_compte('EUROS').solde)


class CotisationSerializer(serializers.ModelSerializer):
    membre_nom = serializers.CharField(source='membre.user.username', read_only=True)

    class Meta:
        model = Cotisation
        fields = ['id', 'membre', 'membre_nom', 'devise', 'montant', 'moyen_paiement', 'mois_concerne', 'date_versement']


class PaiementAchatSerializer(serializers.Serializer):
    code_paiement_lieu = serializers.CharField(max_length=12)
    devise = serializers.ChoiceField(choices=['JUNE', 'EUROS'])
    montant = serializers.DecimalField(max_digits=8, decimal_places=2)
    libelle = serializers.CharField(max_length=255, required=False, default="Achat alimentaire")


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = [
            'reference', 'devise', 'emetteur', 'destinataire', 'montant',
            'type_transaction', 'libelle', 'date_execution'
        ]
        read_only_fields = ['reference', 'date_execution']