from ai_content_platform.app.shared.logging import get_logger

logger = get_logger(__name__)

def handle_content_event(event: dict):
    """Handle content generation events."""
    event_type = event.get("type")
    payload = event.get("payload", {})
    if event_type == "CONTENT_GENERATED":
        handle_content_generated(payload)
    elif event_type == "CONTENT_APPROVED":
        handle_content_approved(payload)
    else:
        logger.error(f"Unknown content event: {event_type}")
        raise ValueError(f"Unknown content event: {event_type}")

def handle_content_generated(payload: dict):
    content_id = payload.get("content_id")
    logger.info(f"[Content Handler] Content generated: {content_id}")

def handle_content_approved(payload: dict):
    content_id = payload.get("content_id")
    logger.info(f"[Content Handler] Content approved: {content_id}")