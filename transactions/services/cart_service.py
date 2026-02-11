"""
Servicio de carrito - encapsula la lógica de negocio del carrito.
"""
from django.conf import settings

from transactions.models import CarritoCompras, ItemCarrito, ItemCarritoCertificacion
from catalog.models import Curso, EstadoCurso, CertificacionIndustria


def obtener_o_crear_carrito(user):
    """
    Retorna el carrito del usuario. Lo crea si no existe.
    """
    carrito, _ = CarritoCompras.objects.get_or_create(user=user)
    return carrito


def agregar_al_carrito(user, curso: Curso, cantidad: int = 1) -> tuple[ItemCarrito | None, str]:
    """
    Agrega un curso al carrito del usuario.
    Retorna (item, mensaje). item es None si falla (ej. curso no disponible).
    """
    if not curso.esta_disponible():
        return None, 'This course is not available for purchase.'
    carrito = obtener_o_crear_carrito(user)
    item, created = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        curso=curso,
        defaults={'cantidad': cantidad}
    )
    if not created:
        item.cantidad += cantidad
        item.save(update_fields=['cantidad'])
    return item, 'Course added to cart.' if created else 'Quantity updated in cart.'


def agregar_certificacion_al_carrito(user, certificacion: CertificacionIndustria, cantidad: int = 1) -> tuple[ItemCarritoCertificacion | None, str]:
    """
    Agrega acceso a una certificación de industria al carrito.
    Retorna (item, mensaje). item es None si la certificación no está activa.
    """
    if not certificacion.activa:
        return None, 'This certification is not available.'
    carrito = obtener_o_crear_carrito(user)
    item, created = ItemCarritoCertificacion.objects.get_or_create(
        carrito=carrito,
        certificacion=certificacion,
        defaults={'cantidad': cantidad}
    )
    if not created:
        item.cantidad += cantidad
        item.save(update_fields=['cantidad'])
    return item, 'Certification access added to cart.' if created else 'Quantity updated in cart.'


def quitar_del_carrito(user, curso_id: int) -> bool:
    """
    Quita un curso del carrito. Retorna True si se eliminó.
    """
    carrito = obtener_o_crear_carrito(user)
    deleted, _ = carrito.items.filter(curso_id=curso_id).delete()
    return deleted > 0


def quitar_certificacion_del_carrito(user, certificacion_slug: str) -> bool:
    """
    Quita una certificación del carrito. Retorna True si se eliminó.
    """
    carrito = obtener_o_crear_carrito(user)
    deleted, _ = carrito.items_certificacion.filter(certificacion__slug=certificacion_slug).delete()
    return deleted > 0


def vaciar_carrito(user) -> None:
    """Elimina todos los items del carrito del usuario (cursos y certificaciones)."""
    carrito = obtener_o_crear_carrito(user)
    carrito.items.all().delete()
    carrito.items_certificacion.all().delete()
