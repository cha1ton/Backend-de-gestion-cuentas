# cuentas/views.py

from django.db.models import Sum, Count
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import BasePermission
from .models import Usuario, Cliente, Proveedor, Factura, Notificacion
from .serializers import UsuarioSerializer, ClienteSerializer, ProveedorSerializer, FacturaSerializer, NotificacionSerializer
from rest_framework import status
from .serializers import RegistroUsuarioSerializer
from rest_framework.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)

# Permiso personalizado para acceso por roles
class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user.rol == 'Administrador'

# Vistas para CRUD de modelos
class UsuarioViewSet(ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        # Permitir que los usuarios normales solo vean su información
        if self.request.user.rol == 'Administrador':
            return Usuario.objects.all()
        return Usuario.objects.filter(id=self.request.user.id)

class ClienteViewSet(ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class ProveedorViewSet(ModelViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer

class FacturaViewSet(ModelViewSet):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer

class NotificacionViewSet(ModelViewSet):
    queryset = Notificacion.objects.all()
    serializer_class = NotificacionSerializer

# Vista para obtener datos del usuario autenticado
class UsuarioActualView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        usuario = request.user
        data = {
            'id': usuario.id,
            'username': usuario.username,
            'email': usuario.email,
            'rol': usuario.rol,
            'permisos': [perm.codename for perm in usuario.user_permissions.all()]
        }
        return Response(data)

class DashboardMetricsView(APIView):
    def get(self, request):
        # Total por cobrar
        total_por_cobrar = Factura.objects.filter(tipo="Cobrar").aggregate(total=Sum('monto_total'))['total'] or 0

        # Total por pagar
        total_por_pagar = Factura.objects.filter(tipo="Pagar").aggregate(total=Sum('monto_total'))['total'] or 0

        # Facturas vencidas
        facturas_vencidas = Factura.objects.filter(estado="Vencida").count()

        # Flujo mensual
        flujo_por_mes = (
            Factura.objects
            .values('fecha_emision__month')
            .annotate(total=Sum('monto_total'))
            .order_by('fecha_emision__month')
        )
        flujo_por_mes_formateado = [
            {"mes": self.get_month_name(entry['fecha_emision__month']), "total": entry['total']}
            for entry in flujo_por_mes
        ]

        data = {
            "totalPorCobrar": total_por_cobrar,
            "totalPorPagar": total_por_pagar,
            "facturasVencidas": facturas_vencidas,
            "flujoPorMes": flujo_por_mes_formateado,
        }
        return Response(data)

    def get_month_name(self, month_number):
        import calendar
        return calendar.month_name[month_number]


# Personalización del login para incluir el rol del usuario en el token
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Agregar el rol del usuario al token
        token['rol'] = user.rol
        return token

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# Permiso personalizado para administrador
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            logger.warning("Intento de acceso no autenticado al endpoint de registro.")
            raise PermissionDenied(detail="Usuario no autenticado.")
        if request.user.rol != 'Administrador':
            logger.warning(f"Acceso denegado para el usuario {request.user.username}. Rol: {request.user.rol}")
            raise PermissionDenied(detail="Acceso denegado. Solo los administradores pueden registrar usuarios.")
        return True

# Vista para registrar usuarios
class RegistroUsuarioView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = RegistroUsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Usuario creado con éxito'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)