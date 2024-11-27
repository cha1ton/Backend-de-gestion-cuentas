from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.core.exceptions import ValidationError
from datetime import date

class Usuario(AbstractUser):
    ROLES = [
        ('Administrador', 'Administrador'),
        ('Contador', 'Contador'),
        ('Gerente', 'Gerente'),
    ]
    rol = models.CharField(max_length=20, choices=ROLES)

    groups = models.ManyToManyField(
        Group,
        related_name="usuario_groups",
        blank=True,
        verbose_name="groups",
        help_text="The groups this user belongs to.",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="usuario_permissions",
        blank=True,
        verbose_name="user permissions",
        help_text="Specific permissions for this user.",
    )


# Modelo de Cliente
class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# Modelo de Proveedor
class Proveedor(models.Model):
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

# Modelo de Factura
class Factura(models.Model):
    TIPO_CHOICES = [
        ('Cobrar', 'Por Cobrar'),
        ('Pagar', 'Por Pagar'),
    ]
    ESTADO_CHOICES = [
        ('Pagada', 'Pagada'),
        ('Pendiente', 'Pendiente'),
        ('Vencida', 'Vencida'),
    ]

    numero_factura = models.CharField(max_length=50, unique=True)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, null=True, blank=True)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, null=True, blank=True)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='Pendiente')

    def save(self, *args, **kwargs):
        # Validación para facturas "Por Cobrar"
        if self.tipo == 'Cobrar' and not self.cliente:
            raise ValidationError("Debe asignar un cliente si el tipo es 'Por Cobrar'")
        if self.tipo == 'Cobrar' and self.proveedor:
            raise ValidationError("No debe asignar un proveedor si el tipo es 'Por Cobrar'")

        # Validación para facturas "Por Pagar"
        if self.tipo == 'Pagar' and not self.proveedor:
            raise ValidationError("Debe asignar un proveedor si el tipo es 'Por Pagar'")
        if self.tipo == 'Pagar' and self.cliente:
            raise ValidationError("No debe asignar un cliente si el tipo es 'Por Pagar'")

        # Actualizar el estado automáticamente
        if self.estado == 'Pendiente' and self.fecha_vencimiento < date.today():
            self.estado = 'Vencida'

        # Llamar al método save original
        super().save(*args, **kwargs)

    @staticmethod
    def actualizar_facturas_vencidas():
        # Actualizar facturas vencidas de forma masiva
        from django.utils.timezone import now
        Factura.objects.filter(
            estado='Pendiente', fecha_vencimiento__lt=now().date()
        ).update(estado='Vencida')

    def __str__(self):
        return f"{self.numero_factura} - {self.tipo}"
    
# Modelo de Notificaciones
class Notificacion(models.Model):
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE)
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    enviada = models.BooleanField(default=False)

    def __str__(self):
        return f"Notificación para {self.factura.numero_factura}"
