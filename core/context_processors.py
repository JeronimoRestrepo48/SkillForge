"""Context processors para templates globales."""

def carrito_cantidad(request):
    """Añade la cantidad de ítems en el carrito para el usuario autenticado."""
    if request.user.is_authenticated:
        from transactions.services import obtener_o_crear_carrito
        carrito = obtener_o_crear_carrito(request.user)
        return {'carrito_cantidad': carrito.cantidad_items()}
    return {'carrito_cantidad': 0}
