from ai_content_platform.app.modules.notifications.services import NotificationService
from ai_content_platform.app.shared.dependencies import get_db
from ai_content_platform.app.shared.logging import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__name__)


def handle_notification_event(event: dict):
    """
    Handle notification events.
    Creates a database session and delegates to service layer.
    """

    try:
        db: Session = get_db().__next__()
        result = NotificationService.process_notification_event(event, db)
        logger.info(f"[Handler] Successfully processed notification: {result}")
        return result
    except Exception as e:
        logger.error(f"[Handler] Error processing notification event: {e}")
        raise
    finally:
        db.close()
