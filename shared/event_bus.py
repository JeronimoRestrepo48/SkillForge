import os
import json
import logging
import redis

logger = logging.getLogger('shared.event_bus')

class RedisEventBus:
    def __init__(self, redis_url=None):
        if not redis_url:
            redis_url = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')
        self.redis = redis.from_url(redis_url, decode_responses=True)

    def publish(self, stream: str, event_type: str, data: dict):
        """
        Publica un evento en un stream de Redis.
        """
        payload = {
            'event_type': event_type,
            'data': json.dumps(data)
        }
        message_id = self.redis.xadd(stream, payload)
        logger.info(f"Published event '{event_type}' to stream '{stream}', ID: {message_id}")
        return message_id

    def consume(self, stream: str, group_name: str, consumer_name: str, block: int = 5000):
        """
        Consume eventos del stream. Si el grupo no existe, lo crea.
        Generador que produce (message_id, event_type, data_dict).
        """
        try:
            self.redis.xgroup_create(stream, group_name, id='0', mkstream=True)
        except redis.exceptions.ResponseError as e:
            if "BUSYGROUP Consumer Group name already exists" not in str(e):
                raise

        while True:
            # '>' lee mensajes nuevos que nunca se han entregado a otros consumidores de este grupo
            try:
                messages = self.redis.xreadgroup(group_name, consumer_name, {stream: '>'}, count=10, block=block)
            except redis.exceptions.ConnectionError as e:
                logger.warning(f"Redis connection error during consume: {e}. Retrying...")
                import time
                time.sleep(2)
                continue
            except redis.exceptions.TimeoutError:
                continue

            for stream_name, msg_list in messages:
                for message_id, payload in msg_list:
                    try:
                        event_type = payload.get('event_type')
                        data_dict = json.loads(payload.get('data', '{}'))
                        yield message_id, event_type, data_dict
                    except Exception as e:
                        logger.error(f"Error parsing event {message_id} from {stream}: {e}")
                    finally:
                        self.redis.xack(stream, group_name, message_id)
