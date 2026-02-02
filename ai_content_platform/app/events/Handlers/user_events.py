from ai_content_platform.app.shared.logging import get_logger

logger = get_logger(__name__)


def handle_user_event(event: dict):
    """Handle user-related events."""
    event_type = event.get("type")
    payload = event.get("payload", {})
    handlers = {
        "USER_REGISTERED": handle_user_registered,
        "USER_PROFILE_UPDATED": handle_user_profile_updated,
    }
    handler = handlers.get(event_type)
    if not handler:
        logger.error(f"Unknown user event type: {event_type}")
        raise ValueError(f"Unknown user event type: {event_type}")
    handler(payload)


def handle_user_registered(payload: dict):
    user_id = payload.get("user_id")
    logger.info(f"[User Handler] User registered: {user_id}")


def handle_user_profile_updated(payload: dict):
    user_id = payload.get("user_id")
    logger.info(f"[User Handler] Profile updated: {user_id}")
