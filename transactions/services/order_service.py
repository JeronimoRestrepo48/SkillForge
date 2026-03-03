"""
Servicio de órdenes - encapsula la lógica de negocio del checkout.
Usa OrderBuilder (patrón Builder) para la creación de la entidad Orden.
"""
from django.db import transaction
from django.utils import timezone

from transactions.models import (
    CarritoCompras,
    Orden,
    Inscripcion,
    Pago,
    Factura,
    EstadoOrden,
    EstadoInscripcion,
    MetodoPago,
    EstadoPago,
)
from transactions.services.cart_service import vaciar_carrito
from transactions.order_builder import OrderBuilder
from catalog.models import AccesoCertificacion


def _generar_numero_factura() -> str:
    """Genera un número de factura único (usado en confirmar_pago_orden)."""
    import random
    import string
    from django.utils import timezone as tz
    ts = tz.now().strftime('%Y%m%d%H%M%S')
    suffix = ''.join(random.choices(string.digits, k=4))
    return f'FAC-{ts}-{suffix}'


def crear_orden_desde_carrito(carrito: CarritoCompras, cupon=None) -> Orden | None:
    """
    Crea una Orden CONFIRMADA desde el carrito usando OrderBuilder.
    Incluye Pago, Factura, Inscripciones, AccesoCertificacion y vacía el carrito.
    """
    builder = OrderBuilder.from_carrito(carrito, cupon)
    if builder is None:
        return None
    builder.set_estado(EstadoOrden.CONFIRMADA)
    return builder.build(
        crear_pago_factura_inscripciones=True,
        vaciar_carrito_callback=vaciar_carrito,
    )


def crear_orden_pendiente_desde_carrito(carrito: CarritoCompras, cupon=None) -> Orden | None:
    """
    Crea una Orden en estado PENDIENTE desde el carrito usando OrderBuilder.
    Solo crea Orden e ítems; no crea Pago, Factura ni inscripciones.
    """
    builder = OrderBuilder.from_carrito(carrito, cupon)
    if builder is None:
        return None
    return builder.build(crear_pago_factura_inscripciones=False)


def confirmar_pago_orden(orden: Orden) -> bool:
    """
    Confirma el pago de una orden PENDIENTE: crea Pago, Factura, Inscripcion, AccesoCertificacion,
    decrementa cupos y vacía el carrito. Idempotente: si ya está CONFIRMADA no hace nada.
    Retorna True si se confirmó, False si ya estaba confirmada o no estaba pendiente.
    """
    if orden.estado != EstadoOrden.PENDIENTE:
        return False

    with transaction.atomic():
        orden.refresh_from_db()
        if orden.estado != EstadoOrden.PENDIENTE:
            return False
        orden.estado = EstadoOrden.CONFIRMADA
        orden.save(update_fields=['estado'])
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
        for item in orden.items.select_related('curso').all():
            Inscripcion.objects.get_or_create(
                user=orden.user,
                curso=item.curso,
                defaults={'orden': orden, 'estado': EstadoInscripcion.ACTIVA},
            )
            item.curso.cupos_disponibles -= item.cantidad
            item.curso.save(update_fields=['cupos_disponibles'])
        for item in orden.items_certificacion.select_related('certificacion').all():
            AccesoCertificacion.objects.get_or_create(
                user=orden.user,
                certificacion=item.certificacion,
            )
        vaciar_carrito(orden.user)
    return True


def marcar_pago_fallido_orden(orden: Orden) -> None:
    """Marca la orden como cancelada y opcionalmente registra un Pago FALLIDO."""
    if orden.estado != EstadoOrden.PENDIENTE:
        return
    with transaction.atomic():
        orden.refresh_from_db()
        if orden.estado != EstadoOrden.PENDIENTE:
            return
        orden.estado = EstadoOrden.CANCELADA
        orden.save(update_fields=['estado'])
        if not hasattr(orden, 'pago') or orden.pago is None:
            Pago.objects.create(
                orden=orden,
                monto=orden.total,
                metodo_pago=MetodoPago.SIMULADO,
                estado=EstadoPago.FALLIDO,
                referencia_transaccion=f'FAIL-{orden.numero_orden}',
                fecha_pago=timezone.now(),
            )
