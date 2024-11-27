# cuentas/serializers.py

from rest_framework import serializers
from .models import Usuario, Cliente, Proveedor, Factura, Notificacion

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'username', 'email', 'rol']

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['id', 'nombre', 'email', 'telefono', 'direccion']

class ProveedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Proveedor
        fields = ['id', 'nombre', 'email', 'telefono', 'direccion']

class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura
        fields = ['id', 'numero_factura', 'tipo', 'cliente', 'proveedor', 'fecha_emision', 'fecha_vencimiento', 'monto_total', 'estado']

    def validate(self, data):
        # Validar lógica para facturas "Por Cobrar"
        if data['tipo'] == 'Cobrar' and not data.get('cliente'):
            raise serializers.ValidationError("Debe asignar un cliente si el tipo es 'Por Cobrar'")
        if data['tipo'] == 'Cobrar' and data.get('proveedor'):
            raise serializers.ValidationError("No debe asignar un proveedor si el tipo es 'Por Cobrar'")
        
        # Validar lógica para facturas "Por Pagar"
        if data['tipo'] == 'Pagar' and not data.get('proveedor'):
            raise serializers.ValidationError("Debe asignar un proveedor si el tipo es 'Por Pagar'")
        if data['tipo'] == 'Pagar' and data.get('cliente'):
            raise serializers.ValidationError("No debe asignar un cliente si el tipo es 'Por Pagar'")

        return data
    
class RegistroUsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'password', 'rol']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Crear un usuario con rol
        usuario = Usuario.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            rol=validated_data['rol']
        )
        return usuario

class NotificacionSerializer(serializers.ModelSerializer):
    factura_numero = serializers.CharField(source='factura.numero_factura', read_only=True)

    class Meta:
        model = Notificacion
        fields = ['id', 'factura', 'factura_numero', 'mensaje', 'fecha_envio', 'enviada']
