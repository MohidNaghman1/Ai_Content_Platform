
from ai_content_platform.app.shared.utils import get_redis_connection
import json
import uuid
from datetime import datetime
from ai_content_platform.app.shared.logging import get_logger

logger = get_logger(__name__)

def publish_event(stream_name: str, event_type: str, payload: dict):
    """
    Generic event publisher for any stream.
    
    :param stream_name: Redis stream name (e.g., 'notifications', 'user_events', 'content_events')
    :param event_type: Event type (e.g., 'USER_REGISTERED', 'CONTENT_CREATED')
    :param payload: Event data
    """
    redis_conn = get_redis_connection()
    event = {
        "id": str(uuid.uuid4()),
        "type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": json.dumps(payload)
    }
    redis_conn.xadd(stream_name, event)
    logger.info(f"[Publisher] Published {event_type} to {stream_name}")