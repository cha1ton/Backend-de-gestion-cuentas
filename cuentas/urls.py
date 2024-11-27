# cuentas/urls.py

from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import DashboardMetricsView
from .views import (
    UsuarioViewSet,
    ClienteViewSet,
    ProveedorViewSet,
    FacturaViewSet,
    NotificacionViewSet,
    UsuarioActualView,
    CustomTokenObtainPairView,
)
from rest_framework_simplejwt.views import TokenRefreshView

# Registrar los endpoints principales con DefaultRouter
router = DefaultRouter()
router.register(r'usuarios', UsuarioViewSet, basename='usuarios')
router.register(r'clientes', ClienteViewSet, basename='clientes')
router.register(r'proveedores', ProveedorViewSet, basename='proveedores')
router.register(r'facturas', FacturaViewSet, basename='facturas')
router.register(r'notificaciones', NotificacionViewSet, basename='notificaciones')

# Agregar rutas personalizadas
urlpatterns = router.urls + [
    path('usuario/', UsuarioActualView.as_view(), name='usuario_actual'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('dashboard-metrics/', DashboardMetricsView.as_view(), name='dashboard-metrics'),
]
