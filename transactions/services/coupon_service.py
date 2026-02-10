"""
Coupon application via session (no FK on cart).
"""
from transactions.models import Cupon

SESSION_KEY_COUPON = 'cupon_codigo'


def aplicar_cupon(request, codigo: str) -> tuple[bool, str, Cupon | None]:
    """
    Validates coupon and stores code in session.
    Returns (success, message, cupon or None).
    """
    codigo = (codigo or '').strip().upper()
    if not codigo:
        return False, 'Ingresa un código de cupón.', None
    try:
        cupon = Cupon.objects.get(codigo__iexact=codigo)
    except Cupon.DoesNotExist:
        return False, 'Cupón no válido.', None
    if not cupon.validar_vigencia():
        return False, 'Este cupón ha expirado o aún no está vigente.', None
    if not cupon.validar_uso_disponible():
        return False, 'Este cupón ya no tiene usos disponibles.', None
    request.session[SESSION_KEY_COUPON] = cupon.codigo
    return True, f'Cupón "{cupon.codigo}" aplicado correctamente.', cupon


def obtener_cupon_aplicado(request) -> Cupon | None:
    """Returns the applied coupon from session if still valid."""
    codigo = request.session.get(SESSION_KEY_COUPON)
    if not codigo:
        return None
    try:
        cupon = Cupon.objects.get(codigo__iexact=codigo)
    except Cupon.DoesNotExist:
        limpiar_cupon(request)
        return None
    if not cupon.validar_vigencia() or not cupon.validar_uso_disponible():
        limpiar_cupon(request)
        return None
    return cupon


def limpiar_cupon(request) -> None:
    """Removes coupon from session."""
    if SESSION_KEY_COUPON in request.session:
        del request.session[SESSION_KEY_COUPON]
