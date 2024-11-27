from django.utils.timezone import now
from .models import Factura

class ActualizarFacturasMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Actualiza automáticamente las facturas vencidas antes de procesar la solicitud
        Factura.actualizar_facturas_vencidas()
        response = self.get_response(request)
        return response
