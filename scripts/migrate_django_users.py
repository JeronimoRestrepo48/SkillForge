"""
migrate_django_users.py — Exporta usuarios de Django PostgreSQL al auth-service PostgreSQL.

Exporta el username, email, rol inferido y el hash pbkdf2_sha256 TAL COMO ESTÁ
desde Django. El auth-service lo aceptará y lo migrará a bcrypt transparentemente
en el primer login del usuario.

Uso (correr desde el directorio raíz del proyecto, con Django activo):
    docker-compose exec web_django python scripts/migrate_django_users.py

O manualmente fuera de Docker (con acceso a ambas BDs):
    DATABASE_URL_DJANGO=postgres://... AUTH_DATABASE_URL=postgres://... python scripts/migrate_django_users.py

NOTA: Este script es idempotente — si el usuario ya existe en auth-db, lo omite.
"""
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configurar Django para acceder al ORM
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.docker")

import django
django.setup()

from django.contrib.auth import get_user_model

# ---------------------------------------------------------------------------
# Importar SQLAlchemy para escribir en auth-db
# ---------------------------------------------------------------------------
try:
    from sqlalchemy import create_engine, Column, Integer, String
    from sqlalchemy.orm import declarative_base, sessionmaker
except ImportError:
    logger.error("sqlalchemy not installed. Run: pip install sqlalchemy psycopg2-binary")
    sys.exit(1)

AUTH_DATABASE_URL = os.getenv(
    "AUTH_DATABASE_URL",
    "postgresql+psycopg2://auth:auth@auth-db:5432/authdb"
)

auth_engine = create_engine(AUTH_DATABASE_URL)
AuthSession = sessionmaker(bind=auth_engine)
AuthBase = declarative_base()


class AuthUser(AuthBase):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    password = Column(String(256), nullable=False)
    email = Column(String(128), nullable=False)
    role = Column(String(32), nullable=False, default="student")


def infer_role(django_user) -> str:
    """Infiere el rol del usuario según flags de Django."""
    if django_user.is_superuser:
        return "admin"
    if django_user.is_staff:
        return "instructor"
    return "student"


def run_migration():
    # Asegurar que la tabla existe en auth-db
    AuthBase.metadata.create_all(bind=auth_engine)

    DjangoUser = get_user_model()
    django_users = DjangoUser.objects.all()

    auth_db = AuthSession()
    migrated, skipped, errors = 0, 0, 0

    try:
        for dj_user in django_users:
            # Comprobar si ya existe en auth-db
            existing = auth_db.query(AuthUser).filter_by(username=dj_user.username).first()
            if existing:
                logger.info("SKIP (already exists): %s", dj_user.username)
                skipped += 1
                continue

            try:
                auth_user = AuthUser(
                    username=dj_user.username,
                    # Copiar el hash pbkdf2 tal como está. El auth-service lo migrará
                    # a bcrypt transparentemente en el primer login.
                    password=dj_user.password,
                    email=dj_user.email or f"{dj_user.username}@skillforge.local",
                    role=infer_role(dj_user),
                )
                auth_db.add(auth_user)
                auth_db.commit()
                logger.info(
                    "MIGRATED: %s (role=%s, hash_type=%s)",
                    dj_user.username,
                    infer_role(dj_user),
                    "pbkdf2" if dj_user.password.startswith("pbkdf2") else "other"
                )
                migrated += 1
            except Exception as exc:
                auth_db.rollback()
                logger.error("ERROR migrating %s: %s", dj_user.username, exc)
                errors += 1
    finally:
        auth_db.close()

    logger.info(
        "=== Migration complete. Migrated: %d | Skipped: %d | Errors: %d ===",
        migrated, skipped, errors
    )

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    run_migration()
