"""
Servicio de carrito - encapsula la lógica de negocio del carrito.
"""
from django.conf import settings

from transactions.models import CarritoCompras, ItemCarrito
from catalog.models import Curso, EstadoCurso


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
        return None, 'El curso no está disponible para compra.'
    carrito = obtener_o_crear_carrito(user)
    item, created = ItemCarrito.objects.get_or_create(
        carrito=carrito,
        curso=curso,
        defaults={'cantidad': cantidad}
    )
    if not created:
        item.cantidad += cantidad
        item.save(update_fields=['cantidad'])
    return item, 'Curso agregado al carrito.' if created else 'Cantidad actualizada en el carrito.'


def quitar_del_carrito(user, curso_id: int) -> bool:
    """
    Quita un curso del carrito. Retorna True si se eliminó.
    """
    carrito = obtener_o_crear_carrito(user)
    deleted, _ = carrito.items.filter(curso_id=curso_id).delete()
    return deleted > 0


def vaciar_carrito(user) -> None:
    """Elimina todos los items del carrito del usuario."""
    carrito = obtener_o_crear_carrito(user)
    carrito.items.all().delete()
