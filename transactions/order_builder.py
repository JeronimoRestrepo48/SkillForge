"""
Patrón Builder para la entidad más compleja del sistema: Orden.
Construye una Orden con sus ItemOrden, ItemOrdenCertificacion y opcionalmente
Pago, Factura, Inscripciones y AccesoCertificacion de forma paso a paso.
"""
import random
import string
from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from transactions.models import (
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
from catalog.models import AccesoCertificacion


def _generar_numero_orden() -> str:
    ts = timezone.now().strftime('%Y%m%d%H%M%S')
    suffix = ''.join(random.choices(string.digits, k=4))
    return f'SF-{ts}-{suffix}'


def _generar_numero_factura() -> str:
    ts = timezone.now().strftime('%Y%m%d%H%M%S')
    suffix = ''.join(random.choices(string.digits, k=4))
    return f'FAC-{ts}-{suffix}'


class OrderBuilder:
    """
    Builder para construir una Orden con ítems de curso, ítems de certificación,
    y opcionalmente pago, factura e inscripciones.
    """

    def __init__(self, user):
        self.user = user
        self.subtotal = Decimal('0')
        self.descuentos = Decimal('0')
        self.total = Decimal('0')
        self.estado = EstadoOrden.PENDIENTE
        self.numero_orden = _generar_numero_orden()
        self._items_curso = []   # list of (curso, precio_unitario, cantidad)
        self._items_cert = []    # list of (certificacion, precio_unitario, cantidad)
        self._cupon = None

    def set_totales(self, subtotal: Decimal, descuentos: Decimal = None, total: Decimal = None):
        self.subtotal = subtotal
        self.descuentos = descuentos if descuentos is not None else Decimal('0')
        self.total = total if total is not None else (subtotal - self.descuentos)
        return self

    def set_estado(self, estado: str):
        self.estado = estado
        return self

    def set_numero_orden(self, numero: str):
        self.numero_orden = numero
        return self

    def add_item_curso(self, curso, precio_unitario: Decimal, cantidad: int = 1):
        self._items_curso.append((curso, precio_unitario, cantidad))
        return self

    def add_item_certificacion(self, certificacion, precio_unitario: Decimal, cantidad: int = 1):
        self._items_cert.append((certificacion, precio_unitario, cantidad))
        return self

    def set_cupon(self, cupon):
        self._cupon = cupon
        return self

    def build(self, crear_pago_factura_inscripciones: bool = False, vaciar_carrito_callback=None):
        """
        Persiste la Orden y sus ítems en la base de datos.
        Si crear_pago_factura_inscripciones es True, crea también Pago, Factura,
        Inscripciones, AccesoCertificacion y decrementa cupos.
        vaciar_carrito_callback: callable(user) opcional para vaciar el carrito al final.
        """
        with transaction.atomic():
            orden = Orden.objects.create(
                user=self.user,
                numero_orden=self.numero_orden,
                estado=self.estado,
                subtotal=self.subtotal,
                descuentos=self.descuentos,
                total=self.total,
            )
            for curso, precio_unitario, cantidad in self._items_curso:
                ItemOrden.objects.create(
                    orden=orden,
                    curso=curso,
                    precio_unitario=precio_unitario,
                    cantidad=cantidad,
                )
            for certificacion, precio_unitario, cantidad in self._items_cert:
                ItemOrdenCertificacion.objects.create(
                    orden=orden,
                    certificacion=certificacion,
                    precio_unitario=precio_unitario,
                    cantidad=cantidad,
                )
            if self._cupon:
                self._cupon.incrementar_uso()

            if crear_pago_factura_inscripciones:
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
                for curso, _precio, cantidad in self._items_curso:
                    Inscripcion.objects.get_or_create(
                        user=self.user,
                        curso=curso,
                        defaults={'orden': orden, 'estado': EstadoInscripcion.ACTIVA},
                    )
                    curso.cupos_disponibles -= cantidad
                    curso.save(update_fields=['cupos_disponibles'])
                for certificacion, _precio, _cantidad in self._items_cert:
                    AccesoCertificacion.objects.get_or_create(
                        user=self.user,
                        certificacion=certificacion,
                    )
                if vaciar_carrito_callback:
                    vaciar_carrito_callback(self.user)

        return orden

    @classmethod
    def from_carrito(cls, carrito, cupon=None):
        """
        Crea un OrderBuilder a partir del carrito y opcional cupón.
        Retorna el builder o None si el carrito está vacío o algún curso no está disponible.
        """
        items = list(carrito.items.select_related('curso').all())
        items_cert = list(carrito.items_certificacion.select_related('certificacion').all())
        if not items and not items_cert:
            return None
        for item in items:
            if not item.curso.esta_disponible():
                return None

        subtotal = sum(
            item.curso.calcular_precio_final() * item.cantidad for item in items
        ) + sum(
            item.certificacion.precio * item.cantidad for item in items_cert
        )
        descuentos = Decimal('0')
        if cupon and cupon.validar_vigencia() and cupon.validar_uso_disponible():
            descuentos = cupon.aplicar_descuento(subtotal)
        total = subtotal - descuentos

        builder = cls(carrito.user).set_totales(subtotal, descuentos, total)
        if cupon:
            builder.set_cupon(cupon)
        for item in items:
            builder.add_item_curso(
                item.curso,
                item.curso.calcular_precio_final(),
                item.cantidad,
            )
        for item in items_cert:
            builder.add_item_certificacion(
                item.certificacion,
                item.certificacion.precio,
                item.cantidad,
            )
        return builder
