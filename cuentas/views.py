# cuentas/views.py

from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import BasePermission
from .models import Usuario, Cliente, Proveedor, Factura, Notificacion
from .serializers import UsuarioSerializer, ClienteSerializer, ProveedorSerializer, FacturaSerializer, NotificacionSerializer

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
