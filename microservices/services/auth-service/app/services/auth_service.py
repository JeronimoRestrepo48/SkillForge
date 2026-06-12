from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.config import settings
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica una contraseña contra su hash.

    Soporta dos esquemas para permitir migración transparente desde Django:
    - bcrypt (hash nativo del auth-service)
    - django_pbkdf2_sha256 (hashes exportados del monolito Django)
    """
    # Hash en formato Django pbkdf2_sha256 → usar verificador nativo
    if hashed_password.startswith("pbkdf2_sha256$"):
        return _verify_django_pbkdf2(plain_password, hashed_password)

    # Hash bcrypt (caso normal) → passlib
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Hash en formato desconocido — no coincide
        return False


def _verify_django_pbkdf2(plain_password: str, encoded: str) -> bool:
    """
    Verifica una contraseña contra el formato Django pbkdf2_sha256.
    No requiere Django instalado — implementación pura con hashlib.
    """
    import hashlib
    import hmac
    import base64

    try:
        _, iterations_str, salt, hash_b64 = encoded.split("$", 3)
        iterations = int(iterations_str)
    except (ValueError, AttributeError):
        return False

    try:
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt.encode("utf-8"),
            iterations,
        )
        computed = base64.b64encode(dk).decode("ascii")
        # Comparación en tiempo constante para evitar timing attacks
        return hmac.compare_digest(computed.strip("="), hash_b64.strip("="))
    except Exception:
        return False


def is_pbkdf2_hash(hashed_password: str) -> bool:
    """Indica si el hash almacenado es formato Django pbkdf2 (pendiente de migrar)."""
    return hashed_password.startswith("pbkdf2_sha256$")


def get_password_hash(password: str) -> str:
    """Hashea una contraseña con bcrypt."""
    return pwd_context.hash(password)


def create_access_token(user: User):
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.JWT_ACCESS_MINUTES)
    to_encode = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(user: User):
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=settings.JWT_REFRESH_DAYS)
    to_encode = {
        "sub": str(user.id),
        "username": user.username,
        "role": user.role,
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
