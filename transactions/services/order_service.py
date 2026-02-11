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
    ItemOrdenCertificacion,
    Inscripcion,
    Pago,
    Factura,
    EstadoOrden,
    EstadoInscripcion,
    MetodoPago,
    EstadoPago,
)
from transactions.services.cart_service import vaciar_carrito
from catalog.models import Curso, EstadoCurso, CertificacionIndustria, AccesoCertificacion


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
    Crea una Orden desde el carrito: ItemOrden por cada curso, ItemOrdenCertificacion por cada
    certificación; Inscripcion por cada curso, AccesoCertificacion por cada certificación;
    descuenta cupos y vacía el carrito.
    Si cupon está presente, aplica descuento y incrementa usos del cupón.
    Retorna la Orden o None si algo falla (ej. sin items, curso sin cupos).
    """
    items = list(carrito.items.select_related('curso').all())
    items_cert = list(carrito.items_certificacion.select_related('certificacion').all())
    if not items and not items_cert:
        return None

    for item in items:
        if not item.curso.esta_disponible():
            return None

    subtotal = sum(
        item.curso.calcular_precio_final() * item.cantidad
        for item in items
    ) + sum(
        item.certificacion.precio * item.cantidad
        for item in items_cert
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
        for item in items_cert:
            ItemOrdenCertificacion.objects.create(
                orden=orden,
                certificacion=item.certificacion,
                precio_unitario=item.certificacion.precio,
                cantidad=item.cantidad,
            )
            AccesoCertificacion.objects.get_or_create(
                user=carrito.user,
                certificacion=item.certificacion,
            )
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


def crear_orden_pendiente_desde_carrito(carrito: CarritoCompras, cupon=None) -> Orden | None:
    """
    Crea una Orden en estado PENDIENTE desde el carrito: ItemOrden e ItemOrdenCertificacion.
    No crea Inscripcion, AccesoCertificacion, Pago, Factura ni vacía el carrito.
    Retorna la Orden o None si algo falla.
    """
    items = list(carrito.items.select_related('curso').all())
    items_cert = list(carrito.items_certificacion.select_related('certificacion').all())
    if not items and not items_cert:
        return None

    for item in items:
        if not item.curso.esta_disponible():
            return None

    subtotal = sum(
        item.curso.calcular_precio_final() * item.cantidad
        for item in items
    ) + sum(
        item.certificacion.precio * item.cantidad
        for item in items_cert
    )
    descuentos = Decimal('0')
    if cupon and cupon.validar_vigencia() and cupon.validar_uso_disponible():
        descuentos = cupon.aplicar_descuento(subtotal)
    total = subtotal - descuentos

    with transaction.atomic():
        orden = Orden.objects.create(
            user=carrito.user,
            numero_orden=_generar_numero_orden(),
            estado=EstadoOrden.PENDIENTE,
            subtotal=subtotal,
            descuentos=descuentos,
            total=total,
        )
        for item in items:
            ItemOrden.objects.create(
                orden=orden,
                curso=item.curso,
                precio_unitario=item.curso.calcular_precio_final(),
                cantidad=item.cantidad,
            )
        for item in items_cert:
            ItemOrdenCertificacion.objects.create(
                orden=orden,
                certificacion=item.certificacion,
                precio_unitario=item.certificacion.precio,
                cantidad=item.cantidad,
            )
        if cupon:
            cupon.incrementar_uso()
    return orden


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
