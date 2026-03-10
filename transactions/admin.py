from django.contrib import admin
from .models import (
    Cupon,
    CarritoCompras,
    ItemCarrito,
    Orden,
    ItemOrden,
    ItemOrdenCertificacion,
    Inscripcion,
    Pago,
    Factura,
)


@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'tipo', 'descuento_porcentaje', 'descuento_fijo', 'fecha_inicio', 'fecha_fin', 'usos_actuales', 'usos_maximos']
    list_filter = ['tipo']
    search_fields = ['codigo']


class ItemCarritoInline(admin.TabularInline):
    model = ItemCarrito
    extra = 0


@admin.register(CarritoCompras)
class CarritoComprasAdmin(admin.ModelAdmin):
    list_display = ['user', 'fecha_creacion']
    search_fields = ['user__username']
    inlines = [ItemCarritoInline]


class ItemOrdenInline(admin.TabularInline):
    model = ItemOrden
    extra = 0


class ItemOrdenCertificacionInline(admin.TabularInline):
    model = ItemOrdenCertificacion
    extra = 0


@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ['numero_orden', 'user', 'estado', 'total', 'fecha_creacion']
    list_filter = ['estado']
    search_fields = ['numero_orden', 'user__username']
    inlines = [ItemOrdenInline, ItemOrdenCertificacionInline]


@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ['user', 'curso', 'estado', 'fecha_inscripcion']
    list_filter = ['estado']
    search_fields = ['user__username', 'curso__titulo']


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ['referencia_transaccion', 'orden', 'monto', 'metodo_pago', 'estado', 'fecha_pago']
    list_filter = ['estado', 'metodo_pago']
    search_fields = ['referencia_transaccion']


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ['numero_factura', 'orden', 'user', 'total', 'fecha_emision']
    search_fields = ['numero_factura']
