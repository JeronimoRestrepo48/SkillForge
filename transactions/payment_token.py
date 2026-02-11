"""Token firmado para el flujo de retorno desde la pasarela simulada (evita falsificación)."""
import json
from django.core import signing

SALT = "transactions.payment_return"
MAX_AGE_SECONDS = 1800  # 30 minutes


def generate_payment_token(numero_orden: str, user_id: int) -> str:
    """Genera un token firmado con numero_orden y user_id. Expira en MAX_AGE_SECONDS."""
    payload = {"numero_orden": numero_orden, "user_id": user_id}
    return signing.dumps(payload, salt=SALT)


def validate_payment_token(token: str) -> tuple[str, int] | None:
    """
    Valida el token y retorna (numero_orden, user_id) o None si inválido/expirado.
    """
    try:
        payload = signing.loads(token, salt=SALT, max_age=MAX_AGE_SECONDS)
        return (payload["numero_orden"], payload["user_id"])
    except (signing.BadSignature, signing.SignatureExpired, KeyError, TypeError):
        return None
