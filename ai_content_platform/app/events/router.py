from ai_content_platform.app.events.Handlers.notification_handler import handle_notification_event
from ai_content_platform.app.events.Handlers.user_events import handle_user_event
from ai_content_platform.app.events.Handlers.content_events import handle_content_event
from ai_content_platform.app.shared.logging import get_logger

logger = get_logger(__name__)

# Map stream names to their handlers
STREAM_HANDLERS = {
    "notifications": handle_notification_event,
    "user_events": handle_user_event,
    "content_events": handle_content_event}

def route_event(stream_name: str, event: dict):
    """
    Routes an event from a stream to the appropriate handler.
    
    :param stream_name: The Redis stream the event came from
    :param event: The event data
    """
    handler = STREAM_HANDLERS.get(stream_name)
    
    if not handler:
        logger.error(f"[Router] No handler registered for stream: {stream_name}")
        raise ValueError(f"Unknown stream: {stream_name}")
    try:
        handler(event)
    except Exception as e:
        logger.error(f"[Router] Error handling event from {stream_name}: {e}")
        raise