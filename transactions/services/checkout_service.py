"""
Servicio de checkout - encapsula el cálculo de totales (subtotal, descuentos, total).
"""
from decimal import Decimal

from transactions.models import CarritoCompras, Cupon


def calcular_totales(carrito: CarritoCompras, cupon=None) -> dict:
    """
    Calcula subtotal, descuentos y total del carrito.
    Si cupon está presente y es válido, aplica el descuento.
    Retorna {'subtotal': Decimal, 'descuentos': Decimal, 'total': Decimal}.
    """
    subtotal = carrito.calcular_subtotal()
    descuentos = Decimal('0')
    if cupon and cupon.validar_vigencia() and cupon.validar_uso_disponible():
        descuentos = cupon.aplicar_descuento(subtotal)
    total = subtotal - descuentos
    return {
        'subtotal': subtotal,
        'descuentos': descuentos,
        'total': total,
    }
