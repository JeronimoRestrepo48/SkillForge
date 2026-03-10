"""Context processors para templates globales."""


def carrito_cantidad(request):
    """Añade la cantidad de ítems en el carrito para el usuario autenticado."""
    if request.user.is_authenticated:
        from transactions.services import obtener_o_crear_carrito
        carrito = obtener_o_crear_carrito(request.user)
        from core.services.notification_service import obtener_no_leidas
        return {
            'carrito_cantidad': carrito.cantidad_items(),
            'unread_notifications_count': obtener_no_leidas(request.user),
        }
    return {'carrito_cantidad': 0, 'unread_notifications_count': 0}
