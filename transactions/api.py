"""
API v1 de transacciones en Django (legacy/monolito).
"""
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from transactions.services import (
    calcular_totales,
    obtener_cupon_aplicado,
    obtener_o_crear_carrito,
)


class CheckoutQuoteV1APIView(APIView):
    """
    GET /api/v1/checkout/quote/
    Retorna la cotización actual del carrito del usuario autenticado.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            carrito = obtener_o_crear_carrito(request.user)
            cupon = obtener_cupon_aplicado(request)
            totales = calcular_totales(carrito, cupon)

            return Response(
                {
                    "version": "v1",
                    "engine": "django-monolith",
                    "items_count": carrito.cantidad_items(),
                    "subtotal": float(totales["subtotal"]),
                    "discounts": float(totales["descuentos"]),
                    "total": float(totales["total"]),
                    "currency": "COP",
                },
                status=status.HTTP_200_OK,
            )
        except ValueError as exc:
            return Response(
                {
                    "error": {
                        "code": "BAD_REQUEST",
                        "message": str(exc),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return Response(
                {
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "Unexpected error while calculating quote.",
                    }
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
