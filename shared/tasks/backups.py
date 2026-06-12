import logging
import subprocess
import os
from celery import shared_task

logger = logging.getLogger('shared.tasks.backups')

@shared_task(bind=True, max_retries=3, default_retry_delay=15)
def backup_databases_task(self):
    """
    Ejecuta el script de backup de bases de datos de forma periódica.
    """
    script_path = os.path.join('/app', 'scripts', 'backup_databases.py')
    if not os.path.exists(script_path):
        logger.warning(f"Backup script not found at {script_path}")
        return {'status': 'skipped', 'reason': 'script_not_found'}

    try:
        subprocess.run(['python', script_path], check=True)
        logger.info('Database backup executed successfully.')
        return {'status': 'ok'}
    except subprocess.CalledProcessError as e:
        logger.error(f'Error executing database backup: {e}')
        raise
