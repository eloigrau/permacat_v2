from django.urls import path, include
from django.views.generic import TemplateView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    MembreViewSet, LieuDeVenteViewSet, CotisationViewSet,
    TransactionViewSet, ProfilConnecteView, SessionLoginView
)
app_name = 'caisse_ssa'

router = DefaultRouter()
router.register(r'membres', MembreViewSet)
router.register(r'lieux', LieuDeVenteViewSet)
router.register(r'cotisations', CotisationViewSet)
router.register(r'transactions', TransactionViewSet)

urlpatterns = [
    path('api/login/', SessionLoginView.as_view(), name='ssa_session_login'),
    path('api/token/', TokenObtainPairView.as_view(), name='ssa_token_obtain'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='ssa_token_refresh'),
    path('api/me/', ProfilConnecteView.as_view(), name='ssa_profil_connecte'),
    path('api/', include(router.urls)),
    path('', TemplateView.as_view(template_name='caisse_ssa/index.html'), name='ssa_app_mobile'),
]