"""
Modelos del dominio Transacciones.
Alineados al diagrama de clases de SkillForge.
"""
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone


class TipoCupon(models.TextChoices):
    """Tipo de descuento del cupón."""
    PORCENTAJE = 'PORCENTAJE', 'Porcentaje'
    MONTO_FIJO = 'MONTO_FIJO', 'Monto fijo'


class Cupon(models.Model):
    """Cupón de descuento (código aplicable en checkout)."""
    codigo = models.CharField(max_length=50, unique=True)
    descuento_porcentaje = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text='Porcentaje de descuento (ej. 10.00 = 10%)'
    )
    descuento_fijo = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Monto fijo a descontar'
    )
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    usos_maximos = models.PositiveIntegerField(default=1)
    usos_actuales = models.PositiveIntegerField(default=0)
    tipo = models.CharField(
        max_length=20,
        choices=TipoCupon.choices,
        default=TipoCupon.PORCENTAJE
    )

    class Meta:
        verbose_name = 'Cupón'
        verbose_name_plural = 'Cupones'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return self.codigo

    def validar_vigencia(self) -> bool:
        now = timezone.now()
        return self.fecha_inicio <= now <= self.fecha_fin

    def validar_uso_disponible(self) -> bool:
        return self.usos_actuales < self.usos_maximos

    def aplicar_descuento(self, subtotal: Decimal) -> Decimal:
        """Retorna el monto a descontar (no el total final)."""
        if self.tipo == TipoCupon.PORCENTAJE and self.descuento_porcentaje:
            return (subtotal * self.descuento_porcentaje / Decimal('100')).quantize(Decimal('0.01'))
        if self.tipo == TipoCupon.MONTO_FIJO and self.descuento_fijo:
            return min(self.descuento_fijo, subtotal)
        return Decimal('0')

    def incrementar_uso(self) -> None:
        self.usos_actuales += 1
        self.save(update_fields=['usos_actuales'])


class CarritoCompras(models.Model):
    """Carrito de compras de un usuario (uno por usuario)."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carrito'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Carrito de compras'
        verbose_name_plural = 'Carritos de compras'

    def __str__(self):
        return f'Carrito de {self.user}'

    def calcular_subtotal(self) -> Decimal:
        """Suma del precio de todos los items (cursos + certificaciones)."""
        total_cursos = sum(
            item.curso.calcular_precio_final() * item.cantidad
            for item in self.items.all().select_related('curso')
        )
        total_certs = sum(
            item.certificacion.precio * item.cantidad
            for item in self.items_certificacion.all().select_related('certificacion')
        )
        return total_cursos + total_certs

    def calcular_total(self) -> Decimal:
        """Total (por ahora igual al subtotal, sin descuentos)."""
        return self.calcular_subtotal()

    def cantidad_items(self) -> int:
        """Número total de ítems (cursos + certificaciones)."""
        return (
            sum(item.cantidad for item in self.items.all())
            + sum(item.cantidad for item in self.items_certificacion.all())
        )


class ItemCarrito(models.Model):
    """Item en el carrito: un curso con cantidad."""
    carrito = models.ForeignKey(
        CarritoCompras,
        on_delete=models.CASCADE,
        related_name='items'
    )
    curso = models.ForeignKey(
        'catalog.Curso',
        on_delete=models.CASCADE,
        related_name='items_carrito'
    )
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Item del carrito'
        verbose_name_plural = 'Items del carrito'
        unique_together = [['carrito', 'curso']]

    def __str__(self):
        return f'{self.curso.titulo} x {self.cantidad}'

    def subtotal(self) -> Decimal:
        return self.curso.calcular_precio_final() * self.cantidad


class ItemCarritoCertificacion(models.Model):
    """Item en el carrito: acceso a una certificación de industria (cantidad normalmente 1)."""
    carrito = models.ForeignKey(
        CarritoCompras,
        on_delete=models.CASCADE,
        related_name='items_certificacion'
    )
    certificacion = models.ForeignKey(
        'catalog.CertificacionIndustria',
        on_delete=models.CASCADE,
        related_name='items_carrito'
    )
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Item carrito (certificación)'
        verbose_name_plural = 'Items carrito (certificaciones)'
        unique_together = [['carrito', 'certificacion']]

    def __str__(self):
        return f'{self.certificacion.nombre} x {self.cantidad}'

    def subtotal(self) -> Decimal:
        return self.certificacion.precio * self.cantidad


class EstadoOrden(models.TextChoices):
    """Estado de una orden."""
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    CONFIRMADA = 'CONFIRMADA', 'Confirmada'
    CANCELADA = 'CANCELADA', 'Cancelada'


class Orden(models.Model):
    """Orden de compra (resultado del checkout)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ordenes'
    )
    numero_orden = models.CharField(max_length=50, unique=True)
    estado = models.CharField(
        max_length=20,
        choices=EstadoOrden.choices,
        default=EstadoOrden.CONFIRMADA
    )
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    descuentos = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.numero_orden


class ItemOrden(models.Model):
    """Item de una orden: curso comprado con precio fijado."""
    orden = models.ForeignKey(
        Orden,
        on_delete=models.CASCADE,
        related_name='items'
    )
    curso = models.ForeignKey(
        'catalog.Curso',
        on_delete=models.PROTECT,
        related_name='items_orden'
    )
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Item de orden'
        verbose_name_plural = 'Items de orden'

    def __str__(self):
        return f'{self.curso.titulo} x {self.cantidad}'

    def subtotal(self) -> Decimal:
        return self.precio_unitario * self.cantidad


class ItemOrdenCertificacion(models.Model):
    """Item de una orden: acceso a certificación de industria comprado."""
    orden = models.ForeignKey(
        Orden,
        on_delete=models.CASCADE,
        related_name='items_certificacion'
    )
    certificacion = models.ForeignKey(
        'catalog.CertificacionIndustria',
        on_delete=models.PROTECT,
        related_name='items_orden'
    )
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    cantidad = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = 'Item orden (certificación)'
        verbose_name_plural = 'Items orden (certificaciones)'

    def __str__(self):
        return f'{self.certificacion.nombre} x {self.cantidad}'

    def subtotal(self) -> Decimal:
        return self.precio_unitario * self.cantidad


class EstadoInscripcion(models.TextChoices):
    """Estado de la inscripción del estudiante en un curso."""
    ACTIVA = 'ACTIVA', 'Activa'
    COMPLETADA = 'COMPLETADA', 'Completada'
    CANCELADA = 'CANCELADA', 'Cancelada'


class Inscripcion(models.Model):
    """Inscripción de un estudiante en un curso (acceso tras compra)."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='inscripciones'
    )
    curso = models.ForeignKey(
        'catalog.Curso',
        on_delete=models.CASCADE,
        related_name='inscripciones'
    )
    orden = models.ForeignKey(
        Orden,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inscripciones'
    )
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        choices=EstadoInscripcion.choices,
        default=EstadoInscripcion.ACTIVA
    )

    class Meta:
        verbose_name = 'Inscripción'
        verbose_name_plural = 'Inscripciones'
        unique_together = [['user', 'curso']]
        ordering = ['-fecha_inscripcion']

    def __str__(self):
        return f'{self.user} en {self.curso.titulo}'


class MetodoPago(models.TextChoices):
    """Método de pago (simulado)."""
    SIMULADO = 'SIMULADO', 'Simulado'
    TARJETA_SIMULADA = 'TARJETA_SIMULADA', 'Tarjeta (simulado)'


class EstadoPago(models.TextChoices):
    """Estado del pago."""
    PENDIENTE = 'PENDIENTE', 'Pendiente'
    COMPLETADO = 'COMPLETADO', 'Completado'
    FALLIDO = 'FALLIDO', 'Fallido'
    REEMBOLSADO = 'REEMBOLSADO', 'Reembolsado'


class Pago(models.Model):
    """Pago asociado a una orden (100% simulado, sin pasarela real)."""
    orden = models.OneToOneField(
        Orden,
        on_delete=models.CASCADE,
        related_name='pago'
    )
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    metodo_pago = models.CharField(
        max_length=30,
        choices=MetodoPago.choices,
        default=MetodoPago.SIMULADO
    )
    estado = models.CharField(
        max_length=20,
        choices=EstadoPago.choices,
        default=EstadoPago.COMPLETADO
    )
    referencia_transaccion = models.CharField(max_length=100, blank=True)
    fecha_pago = models.DateTimeField()

    class Meta:
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return f'{self.referencia_transaccion} - {self.orden.numero_orden}'


class Factura(models.Model):
    """Factura simulada asociada a una orden (solo almacenamiento)."""
    orden = models.OneToOneField(
        Orden,
        on_delete=models.CASCADE,
        related_name='factura'
    )
    numero_factura = models.CharField(max_length=50, unique=True)
    fecha_emision = models.DateTimeField()
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    descuentos = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    total = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0'))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='facturas'
    )

    class Meta:
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'

    def __str__(self):
        return self.numero_factura
