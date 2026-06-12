import os
import logging
import boto3
from botocore.exceptions import ClientError
from celery import shared_task

logger = logging.getLogger('shared.tasks.notifications')

@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def enviar_notificacion_orden_async(self, data: dict):
    """
    Crea notificación y envía email tras confirmar una orden (proceso en background).
    Usando AWS SES directamente con boto3.
    """
    user_email = data.get('email')
    user_name = data.get('nombre_usuario', 'Estudiante')
    numero_orden = data.get('numero_orden', '')

    if not user_email:
        logger.warning('enviar_notificacion_orden_async: email not provided')
        return {'status': 'skipped', 'reason': 'email_missing'}

    sender = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@skillforge.local')
    aws_region = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')

    subject = f"Confirmación de tu orden {numero_orden} en SkillForge"
    body_text = (f"Hola {user_name},\r\n"
                 f"Tu orden {numero_orden} ha sido procesada exitosamente.\r\n"
                 "Gracias por confiar en SkillForge. ¡Empieza a aprender hoy mismo!")
    
    body_html = f"""<html>
    <head></head>
    <body>
      <h1>Confirmación de Orden</h1>
      <p>Hola {user_name},</p>
      <p>Tu orden <strong>{numero_orden}</strong> ha sido procesada exitosamente.</p>
      <p>Gracias por confiar en SkillForge. ¡Empieza a aprender hoy mismo!</p>
    </body>
    </html>
    """

    try:
        client = boto3.client('ses',
                              region_name=aws_region,
                              aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                              aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'))

        response = client.send_email(
            Destination={
                'ToAddresses': [user_email],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': "UTF-8",
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': "UTF-8",
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': "UTF-8",
                    'Data': subject,
                },
            },
            Source=sender,
        )
        logger.info(f"Email sent to {user_email} via SES. Message ID: {response['MessageId']}")
        return {'status': 'ok', 'email': user_email, 'order': numero_orden, 'message_id': response['MessageId']}

    except ClientError as e:
        logger.error(f"SES Error sending email to {user_email}: {e.response['Error']['Message']}")
        raise
    except Exception as e:
        logger.error(f"Error sending email to {user_email}: {e}")
        raise
