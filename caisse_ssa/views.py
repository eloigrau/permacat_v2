from decimal import Decimal
from django.http import HttpResponse
from django.db import transaction as db_transaction
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError as DRFValidationError
from .services import calculer_prochain_du, distribuer_dividende_universel

from .models import MembreSSA, LieuDeVente, CompteMonnaieLocale, Cotisation, Transaction
from .serializers import (
    MembreSSASerializer, LieuDeVenteSerializer, CotisationSerializer,
    TransactionSerializer, PaiementAchatSerializer
)
from django.utils import timezone
from caisse_ssa.pdf_reports import generer_pdf_bilan_mensuel
from django.contrib.auth import authenticate, login as django_login
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response


class EstAdministrateurCaisse(permissions.BasePermission):
    """Autorise uniquement les membres du Conseil Collégial ou superusers."""
    message = "Action réservée aux administrateurs de la caisse (Conseil)."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_staff:
            return True
        profil_ssa = getattr(request.user, 'profil_ssa', None)
        return bool(profil_ssa and profil_ssa.est_membre_conseil)


class EstAdminCaisseOuLectureSeule(permissions.BasePermission):
    """
    Lecture (GET) autorisée à tout membre connecté ;
    Écriture/Modification (POST, PUT, PATCH, DELETE) réservée aux administrateurs de la caisse.
    """
    message = "Seuls les administrateurs de la caisse peuvent effectuer cette modification."

    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True
        profil_ssa = getattr(request.user, 'profil_ssa', None)
        return bool(profil_ssa and profil_ssa.role == 'CONSEIL')

class EstConseilCollegial(permissions.BasePermission):
    """Autorise uniquement les membres du Conseil Collégial ou superusers."""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if request.user.is_staff:
            return True
        profil_ssa = getattr(request.user, 'profil_ssa', None)
        return bool(profil_ssa and profil_ssa.role == 'CONSEIL')

class ProfilConnecteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        profil_ssa, _ = MembreSSA.objects.get_or_create(
            user=user,
            defaults={'est_membre_conseil': user.is_staff}
        )
        compte_june = profil_ssa.get_compte('JUNE')
        compte_euros = profil_ssa.get_compte('EUROS')

        lieux = LieuDeVente.objects.filter(gestionnaire=profil_ssa)
        est_admin = profil_ssa.est_membre_conseil or user.is_staff

        caisse_june_solde = CompteMonnaieLocale.get_caisse_centrale('JUNE').solde if est_admin else None
        caisse_euros_solde = CompteMonnaieLocale.get_caisse_centrale('EUROS').solde if est_admin else None

        return Response({
            "id": profil_ssa.id,
            "username": user.username,
            "est_membre_conseil": est_admin,
            "solde_june": compte_june.solde,
            "solde_euros": compte_euros.solde,
            "caisse_june_solde": caisse_june_solde,
            "caisse_euros_solde": caisse_euros_solde,
            "lieux_geres": LieuDeVenteSerializer(lieux, many=True).data
        })


class CotisationViewSet(viewsets.ModelViewSet):
    queryset = Cotisation.objects.select_related('membre__user').all().order_by('-date_versement')
    serializer_class = CotisationSerializer
    permission_classes = [EstAdminCaisseOuLectureSeule]

    def get_queryset(self):
        user = self.request.user
        profil_ssa = getattr(user, 'profil_ssa', None)
        if user.is_staff or (profil_ssa and profil_ssa.role == 'CONSEIL'):
            return self.queryset
        return self.queryset.filter(membre__user=user)

    def perform_create(self, serializer):
        try:
            serializer.save()
        except DjangoValidationError as e:
            # Renvoie proprement l'erreur si solde négatif ou insuffisant
            raise DRFValidationError({"detail": e.messages[0]})


class MembreViewSet(viewsets.ModelViewSet):
    # CORRECTION : On ne garde que 'user' dans select_related
    queryset = MembreSSA.objects.select_related('user').all()
    serializer_class = MembreSSASerializer
    permission_classes = [EstAdminCaisseOuLectureSeule]

    def perform_create(self, serializer):
        membre_ssa = serializer.save()
        # Les comptes JUNE et EUROS sont créés automatiquement par le serializer ou les méthodes
        membre_ssa.get_compte('JUNE')
        membre_ssa.get_compte('EUROS')

    def get_queryset(self):
        user = self.request.user
        profil_ssa = getattr(user, 'profil_ssa', None)
        # Seuls les administrateurs voient la liste complète de tous les membres
        if user.is_staff or (profil_ssa and profil_ssa.role == 'CONSEIL'):
            return self.queryset
        return self.queryset.filter(user=user)


class LieuDeVenteViewSet(viewsets.ModelViewSet):
    queryset = LieuDeVente.objects.all()
    serializer_class = LieuDeVenteSerializer
    permission_classes = [EstAdminCaisseOuLectureSeule]
    filterset_fields = ['est_conventionne', 'type_lieu']

    def perform_create(self, serializer):
        lieu = serializer.save()
        CompteMonnaieLocale.objects.get_or_create(
            lieu_de_vente=lieu,
            defaults={'type_compte': 'PROFESSIONNEL'}
        )


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Transaction.objects.all().order_by('-date_execution')
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        profil_ssa = getattr(user, 'profil_ssa', None)
        if user.is_staff or (profil_ssa and profil_ssa.role == 'CONSEIL'):
            return self.queryset
        # Un membre non-admin ne voit que les mouvements qui concernent son compte ou ses stands
        from django.db.models import Q
        return self.queryset.filter(
            Q(emetteur__proprietaire=profil_ssa) |
            Q(destinataire__proprietaire=profil_ssa) |
            Q(destinataire__lieu_de_vente__gestionnaire=profil_ssa)
        )

    @action(detail=False, methods=['post'], url_path='payer-lieu')
    def payer_lieu(self, request):
        serializer = PaiementAchatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code_paiement_lieu'].upper()
        devise = serializer.validated_data['devise']
        montant = serializer.validated_data['montant']
        libelle = serializer.validated_data['libelle']

        profil_ssa = getattr(request.user, 'profil_ssa', None)
        if not profil_ssa:
            return Response({"detail": "Profil SSA introuvable."}, status=status.HTTP_400_BAD_REQUEST)

        # Récupère le compte émetteur (fonctionne qu'il soit participant ou producteur)
        compte_emetteur = profil_ssa.get_compte(devise)

        try:
            lieu = LieuDeVente.objects.get(code_paiement=code)
            compte_destinataire = lieu.get_compte(devise)
        except LieuDeVente.DoesNotExist:
            return Response({"detail": "Code lieu de vente introuvable."}, status=status.HTTP_404_NOT_FOUND)

        # Empêche un lieu de se payer lui-même
        if lieu.gestionnaire == profil_ssa:
            return Response({"detail": "Vous ne pouvez pas effectuer un paiement vers votre propre stand."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            tx = Transaction.objects.create(
                emetteur=compte_emetteur,
                destinataire=compte_destinataire,
                devise=devise,
                montant=montant,
                type_transaction='PAIEMENT_ACHAT',
                libelle=f"{lieu.nom} - {libelle}"
            )
        except DjangoValidationError as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        return Response(TransactionSerializer(tx).data, status=status.HTTP_201_CREATED)

    @action(
        detail=False, methods=['post'],
        url_path='distribuer-allocations',
        permission_classes=[EstAdministrateurCaisse]
    )
    def distribuer_allocations(self, request):
        devise = request.data.get('devise', 'JUNE')
        if devise not in ['JUNE', 'EUROS']:
            return Response({"detail": "Devise invalide."}, status=status.HTTP_400_BAD_REQUEST)

        montant = Decimal(str(request.data.get('montant_allocation', '0')))
        mois = request.data.get('mois', 'Mensuel')

        if montant <= 0:
            return Response({"detail": "Montant invalide."}, status=status.HTTP_400_BAD_REQUEST)

        caisse_centrale = CompteMonnaieLocale.get_caisse_centrale(devise)
        allocataires = MembreSSA.objects.filter(est_allocataire=True, user__is_active=True)
        total_requis = montant * allocataires.count()

        if caisse_centrale.solde < total_requis:
            return Response(
                {
                    "detail": f"Fonds insuffisants dans la caisse {devise} ({caisse_centrale.solde} dispo / {total_requis} requis)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        with db_transaction.atomic():
            for membre_ssa in allocataires:
                Transaction.objects.create(
                    emetteur=caisse_centrale,
                    destinataire=membre_ssa.get_compte(devise),
                    devise=devise,
                    montant=montant,
                    type_transaction='ALLOCATION',
                    libelle=f"Allocation SSA ({devise}) - {mois}"
                )

        return Response({
            "message": f"{allocataires.count()} allocations de {montant} {devise} versées.",
            "nouveau_solde_caisse": caisse_centrale.solde
        })

    @action(
        detail=False, methods=['post'],
        url_path='reconvertir',
        permission_classes=[EstAdministrateurCaisse]
    )
    def reconvertir(self, request):
        lieu_id = request.data.get('lieu_id')
        montant = Decimal(str(request.data.get('montant', '0')))
        try:
            lieu = LieuDeVente.objects.get(id=lieu_id)
            compte_pro = lieu.get_compte('EUROS')
        except (LieuDeVente.DoesNotExist, CompteMonnaieLocale.DoesNotExist):
            return Response({"detail": "Lieu introuvable."}, status=status.HTTP_404_NOT_FOUND)

        caisse_centrale = CompteMonnaieLocale.get_caisse_centrale('EUROS')

        try:
            Transaction.objects.create(
                emetteur=compte_pro,
                destinataire=caisse_centrale,
                montant=montant,
                type_transaction='RECONVERSION',
                libelle=f"Reconversion € - {lieu.nom}"
            )
        except DjangoValidationError as e:
            return Response({"detail": e.messages}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": f"Reconversion de {montant} ML validée pour {lieu.nom}.",
            "nouveau_solde_pro": compte_pro.solde
        }, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=['get', 'post'],
        url_path='dividende-universel',
        permission_classes=[EstAdministrateurCaisse]
    )
    def dividende_universel(self, request):
        if request.method == 'GET':
            du_unitaire, masse_totale, nb_membres = calculer_prochain_du()
            moyenne_m_sur_n = (masse_totale / nb_membres) if nb_membres > 0 else Decimal('0.00')
            return Response({
                "masse_monetaire_totale": masse_totale,
                "nombre_cocreateurs": nb_membres,
                "moyenne_M_sur_N": round(moyenne_m_sur_n, 2),
                "prochain_du_estime": du_unitaire
            })

        journal, message = distribuer_dividende_universel()
        if not journal:
            return Response({"detail": message}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            "message": message,
            "montant_du": journal.montant_du_unitaire,
            "nombre_cocreateurs": journal.nombre_cocreateurs
        }, status=status.HTTP_201_CREATED)

    @action(
        detail=False, methods=['get'],
        url_path='bilan-pdf',
        permission_classes=[EstAdministrateurCaisse]
    )
    def bilan_pdf(self, request):
        """Télécharge le bilan PDF pour ?annee=2026&mois=11 (mois en cours par défaut)."""
        now = timezone.localdate()
        annee = int(request.query_params.get('annee', now.year))
        mois = int(request.query_params.get('mois', now.month))

        pdf_bytes = generer_pdf_bilan_mensuel(annee, mois, sauvegarder_fichier=True)
        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="bilan_caisse_SSA_{annee}_{mois:02d}.pdf"'
        return response



class SessionLoginView(APIView):
    """Connexion via la session standard Django (compatible username ou email)."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        identifiant = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=identifiant, password=password)
        if user is not None:
            django_login(request, user)
            return Response({"message": "Connecté"})
        return Response({"detail": "Identifiant ou mot de passe incorrect."}, status=status.HTTP_401_UNAUTHORIZED)


