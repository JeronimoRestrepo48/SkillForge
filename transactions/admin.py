from django.contrib import admin
from .models import Cupon, CarritoCompras, ItemCarrito, Orden, ItemOrden, Inscripcion, Pago, Factura


@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'tipo', 'descuento_porcentaje', 'descuento_fijo', 'fecha_inicio', 'fecha_fin', 'usos_actuales', 'usos_maximos']
    list_filter = ['tipo']


admin.site.register(CarritoCompras)
admin.site.register(ItemCarrito)
admin.site.register(Orden)
admin.site.register(ItemOrden)
admin.site.register(Inscripcion)
admin.site.register(Pago)
admin.site.register(Factura)
