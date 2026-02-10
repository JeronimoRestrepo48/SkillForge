"""
Servicio de órdenes - encapsula la lógica de negocio del checkout.
"""
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from transactions.models import (
    CarritoCompras,
    Orden,
    ItemOrden,
    Inscripcion,
    Pago,
    Factura,
    EstadoOrden,
    EstadoInscripcion,
    MetodoPago,
    EstadoPago,
)
from transactions.services.cart_service import vaciar_carrito
from catalog.models import Curso, EstadoCurso


def _generar_numero_orden() -> str:
    """Genera un número de orden único (timestamp + random suffix)."""
    import random
    import string
    ts = timezone.now().strftime('%Y%m%d%H%M%S')
    suffix = ''.join(random.choices(string.digits, k=4))
    return f'SF-{ts}-{suffix}'


def _generar_numero_factura() -> str:
    """Genera un número de factura único."""
    import random
    import string
    ts = timezone.now().strftime('%Y%m%d%H%M%S')
    suffix = ''.join(random.choices(string.digits, k=4))
    return f'FAC-{ts}-{suffix}'


def crear_orden_desde_carrito(carrito: CarritoCompras, cupon=None) -> Orden | None:
    """
    Crea una Orden desde el carrito, ItemOrden por cada item,
    Inscripcion por cada curso comprado, descuenta cupos y vacía el carrito.
    Si cupon está presente, aplica descuento y incrementa usos del cupón.
    Retorna la Orden o None si algo falla (ej. sin items, curso sin cupos).
    """
    items = list(carrito.items.select_related('curso').all())
    if not items:
        return None

    for item in items:
        if not item.curso.esta_disponible():
            return None

    subtotal = sum(
        item.curso.calcular_precio_final() * item.cantidad
        for item in items
    )
    descuentos = Decimal('0')
    if cupon and cupon.validar_vigencia() and cupon.validar_uso_disponible():
        descuentos = cupon.aplicar_descuento(subtotal)
    total = subtotal - descuentos

    with transaction.atomic():
        orden = Orden.objects.create(
            user=carrito.user,
            numero_orden=_generar_numero_orden(),
            estado=EstadoOrden.CONFIRMADA,
            subtotal=subtotal,
            descuentos=descuentos,
            total=total,
        )
        for item in items:
            precio = item.curso.calcular_precio_final()
            ItemOrden.objects.create(
                orden=orden,
                curso=item.curso,
                precio_unitario=precio,
                cantidad=item.cantidad,
            )
            Inscripcion.objects.get_or_create(
                user=carrito.user,
                curso=item.curso,
                defaults={
                    'orden': orden,
                    'estado': EstadoInscripcion.ACTIVA,
                }
            )
            curso = item.curso
            curso.cupos_disponibles -= item.cantidad
            curso.save(update_fields=['cupos_disponibles'])
        if cupon:
            cupon.incrementar_uso()
        # Pago y factura simulados
        Pago.objects.create(
            orden=orden,
            monto=orden.total,
            metodo_pago=MetodoPago.SIMULADO,
            estado=EstadoPago.COMPLETADO,
            referencia_transaccion=f'SIM-{orden.numero_orden}',
            fecha_pago=timezone.now(),
        )
        Factura.objects.create(
            orden=orden,
            numero_factura=_generar_numero_factura(),
            fecha_emision=timezone.now(),
            subtotal=orden.subtotal,
            descuentos=orden.descuentos,
            total=orden.total,
            user=orden.user,
        )
        vaciar_carrito(carrito.user)
    return orden
