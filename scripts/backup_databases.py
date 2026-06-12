"""
backup_databases.py — Backup de todas las bases de datos PostgreSQL del ecosistema SkillForge.
Cubre: Django (db), auth-db, catalog-db, transactions-db.
Comprime cada dump con gzip y, si AWS_BACKUP_BUCKET está configurado, sube a S3.

Uso local (desarrollo):
    python scripts/backup_databases.py

Uso desde Celery (producción):
    Invocado automáticamente por core.tasks.backup_databases_task a las 3 AM.
"""
import os
import subprocess
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuración de las bases de datos a respaldar
# Cada entrada: (nombre_lógico, host_docker, puerto, usuario, password, dbname)
# ---------------------------------------------------------------------------
DATABASES_TO_BACKUP = [
    {
        "name": "django",
        "host": os.getenv("POSTGRES_HOST", "db"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "user": os.getenv("POSTGRES_USER", "skillforge"),
        "password": os.getenv("POSTGRES_PASSWORD", "skillforge"),
        "dbname": os.getenv("POSTGRES_DB", "skillforge"),
    },
    {
        "name": "auth",
        "host": os.getenv("AUTH_DB_HOST", "auth-db"),
        "port": os.getenv("AUTH_DB_PORT", "5432"),
        "user": os.getenv("AUTH_DB_USER", "auth"),
        "password": os.getenv("AUTH_DB_PASSWORD", "auth"),
        "dbname": os.getenv("AUTH_DB_NAME", "authdb"),
    },
    {
        "name": "catalog",
        "host": os.getenv("CATALOG_DB_HOST", "catalog-db"),
        "port": os.getenv("CATALOG_DB_PORT", "5432"),
        "user": os.getenv("CATALOG_DB_USER", "catalog"),
        "password": os.getenv("CATALOG_DB_PASSWORD", "catalog"),
        "dbname": os.getenv("CATALOG_DB_NAME", "catalogdb"),
    },
    {
        "name": "transactions",
        "host": os.getenv("TRANSACTIONS_DB_HOST", "transactions-db"),
        "port": os.getenv("TRANSACTIONS_DB_PORT", "5432"),
        "user": os.getenv("TRANSACTIONS_DB_USER", "transactions"),
        "password": os.getenv("TRANSACTIONS_DB_PASSWORD", "transactions"),
        "dbname": os.getenv("TRANSACTIONS_DB_NAME", "transactionsdb"),
    },
]


def _dump_database(db_cfg: dict, backup_dir: Path, date_str: str) -> Path | None:
    """
    Ejecuta pg_dump para una base de datos y comprime el resultado con gzip.
    Retorna la ruta del archivo generado, o None si falló.
    """
    filename = backup_dir / f"backup_{db_cfg['name']}_{date_str}.sql.gz"
    env = os.environ.copy()
    env["PGPASSWORD"] = db_cfg["password"]

    cmd = (
        f"pg_dump -U {db_cfg['user']} -h {db_cfg['host']} "
        f"-p {db_cfg['port']} {db_cfg['dbname']}"
    )

    try:
        dump = subprocess.run(
            cmd, shell=True, env=env, check=True,
            capture_output=True
        )
        # Comprimir con gzip
        import gzip
        with gzip.open(str(filename), "wb") as f:
            f.write(dump.stdout)

        size_kb = filename.stat().st_size // 1024
        logger.info(
            "Backup OK: %s → %s (%d KB)",
            db_cfg["name"], filename.name, size_kb
        )
        return filename
    except subprocess.CalledProcessError as exc:
        logger.error(
            "Backup FAILED for %s: %s | stderr: %s",
            db_cfg["name"], exc, exc.stderr.decode(errors="replace") if exc.stderr else ""
        )
        return None


def _upload_to_s3(filepath: Path, bucket: str, prefix: str = "backups/") -> bool:
    """
    Sube un archivo de backup a S3.
    Requiere: boto3 instalado y credenciales AWS configuradas
    (env vars AWS_ACCESS_KEY_ID / AWS_SECRET_ACCESS_KEY o rol IAM).
    """
    try:
        import boto3
        s3 = boto3.client("s3")
        s3_key = f"{prefix}{filepath.name}"
        s3.upload_file(str(filepath), bucket, s3_key)
        logger.info("S3 upload OK: s3://%s/%s", bucket, s3_key)
        return True
    except ImportError:
        logger.warning("boto3 not installed — skipping S3 upload for %s", filepath.name)
        return False
    except Exception as exc:
        logger.error("S3 upload FAILED for %s: %s", filepath.name, exc)
        return False


def run_backup():
    """
    Punto de entrada principal: hace backup de todas las BDs y opcionalmente
    sube a S3 si AWS_BACKUP_BUCKET está configurado en el entorno.
    """
    date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path(os.getenv("BACKUP_DIR", "/tmp/skillforge_backups"))
    backup_dir.mkdir(parents=True, exist_ok=True)

    s3_bucket = os.getenv("AWS_BACKUP_BUCKET", "")

    results = {"ok": [], "failed": []}

    logger.info("=== SkillForge DB Backup started — %s ===", date_str)

    for db_cfg in DATABASES_TO_BACKUP:
        filepath = _dump_database(db_cfg, backup_dir, date_str)
        if filepath is None:
            results["failed"].append(db_cfg["name"])
            continue

        results["ok"].append(db_cfg["name"])

        # Subir a S3 si está configurado
        if s3_bucket:
            _upload_to_s3(filepath, s3_bucket)
        else:
            logger.info(
                "AWS_BACKUP_BUCKET not set — backup kept locally at %s", filepath
            )

    logger.info(
        "=== Backup finished. OK: %s | FAILED: %s ===",
        results["ok"], results["failed"]
    )

    if results["failed"]:
        raise RuntimeError(
            f"Backup failed for databases: {results['failed']}"
        )

    return results


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        run_backup()
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
