
# app/modules/notifications/services.py
from ai_content_platform.app.modules.notifications.models import Notification, InAppNotificationStore
from ai_content_platform.app.modules.users.models import User
from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from datetime import datetime
from ai_content_platform.app.shared.logging import get_logger
logger = get_logger(__name__)


class NotificationService:
    """
    Handles all notification business logic.
    Supports email (simulated) and in-app notifications.
    """
    
    def __init__(self, db: Session = None):
        self.db = db
    
    def get_user_preferences(self, user_id: int) -> Dict[str, bool]:
        """
        Fetch user notification preferences from the database.
        Returns which notification channels are enabled.
        """
        logger.info(f"Fetching notification preferences for user {user_id}")
        try:
            if self.db:
                user = self.db.query(User).filter(User.id == user_id).first()
                if user:
                    return {
                        "email_notifications": getattr(user, "email_notifications", True),
                        "in_app_notifications": getattr(user, "in_app_notifications", True)
                    }
            # Default: all notifications enabled
            return {
                "email_notifications": True,
                "in_app_notifications": True
            }
        except Exception as e:
            logger.error(f"Error fetching user preferences for user {user_id}: {e}", exc_info=True)
            return {
                "email_notifications": True,
                "in_app_notifications": True
            }
    
    def process_notification_event(self, event: dict) -> Dict:
        """
        Main entry point for processing notification events.
        Determines which channels to use based on event type and user preferences.
        """
        try:
            event_type = event.get("type")
            payload = event.get("payload", {})
            user_id = payload.get("user_id")
            message = payload.get("message")
            email = payload.get("email")
            # Validation
            if not user_id or not message:
                logger.error("[Notification] Invalid event data: missing user_id or message")
                raise ValueError("Missing required fields: user_id or message")
            # Get user preferences
            preferences = self.get_user_preferences(user_id)
            results = {
                "user_id": user_id,
                "event_type": event_type,
                "sent": [],
                "skipped": []
            }
            # Process based on event type
            if event_type == "email":
                if preferences.get("email_notifications"):
                    self.send_email_notification(user_id, message, email)
                    results["sent"].append("email")
                else:
                    results["skipped"].append("email (disabled in preferences)")
                    logger.info(f"[Notification] Skipped email for user {user_id} due to preferences")
            elif event_type == "in_app":
                if preferences.get("in_app_notifications"):
                    self.send_in_app_notification(user_id, message)
                    results["sent"].append("in_app")
                else:
                    results["skipped"].append("in_app (disabled in preferences)")
                    logger.info(f"[Notification] Skipped in_app for user {user_id} due to preferences")
            elif event_type == "notification":
                # Generic notification: send to both channels if enabled
                if preferences.get("in_app_notifications"):
                    self.send_in_app_notification(user_id, message)
                    results["sent"].append("in_app")
                if preferences.get("email_notifications"):
                    self.send_email_notification(user_id, message, email)
                    results["sent"].append("email")
            else:
                logger.error(f"[Notification] Unknown event type: {event_type}")
                raise ValueError(f"Unknown notification event type: {event_type}")
            logger.info(f"[NotificationService] Processed event for user {user_id}: {results}")
            return results
        except Exception as e:
            logger.error(f"Error processing notification event: {e}", exc_info=True)
            raise
    
    def send_email_notification(
        self, 
        user_id: int, 
        message: str, 
        to_email: Optional[str] = None
    ) -> Notification:
        """
        Send email notification (simulated).
        Logs the email in the database.
        """
        try:
            # Get user email if not provided
            if not to_email:
                to_email = self._get_user_email(user_id)
            # Simulate sending email
            logger.info(f"[EMAIL] To: {to_email} | User ID: {user_id} | Message: {message}")
            # Log email in database
            email_log = Notification(
                user_id=user_id,
                message=message,
                notif_type="email",
                read=False
            )
            if self.db:
                self.db.add(email_log)
                self.db.commit()
                self.db.refresh(email_log)
            # Add to in-memory store for fast access
            InAppNotificationStore.add_notification(email_log)
            return email_log
        except Exception as e:
            logger.error(f"Error sending email notification to user {user_id}: {e}", exc_info=True)
            raise
    
    def send_in_app_notification(
        self, 
        user_id: int, 
        message: str
    ) -> Notification:
        """
        Create and store in-app notification.
        Stores in both database and in-memory cache.
        """
        try:
            logger.info(f"[In-App] Creating notification for user {user_id}: {message}")
            # Create notification object
            notif = Notification(
                user_id=user_id,
                message=message,
                notif_type="in_app",
                read=False
            )
            # Save to database
            if self.db:
                self.db.add(notif)
                self.db.commit()
                self.db.refresh(notif)
            # Add to in-memory store for fast access
            InAppNotificationStore.add_notification(notif)
            logger.info(f"[In-App] Notification created with ID: {notif.id if notif.id else 'N/A'}")
            return notif
        except Exception as e:
            logger.error(f"Error sending in-app notification to user {user_id}: {e}", exc_info=True)
            raise
    
    def get_user_notifications(
        self, 
        user_id: int, 
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """
        Get in-app notifications for a user.
        First checks in-memory store, falls back to database.
        """
        logger.info(f"Fetching notifications for user {user_id}, unread_only={unread_only}, limit={limit}")
        try:
            # Try in-memory store first (faster)
            notifications = InAppNotificationStore.get_user_notifications(user_id)
            if unread_only:
                notifications = [n for n in notifications if not n.read]
            if notifications:
                return notifications[:limit]
            # Fall back to database
            if not self.db:
                return []
            query = self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.notif_type == "in_app"
            )
            if unread_only:
                query = query.filter(Notification.read == False)
            return query.order_by(Notification.created_at.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error fetching notifications for user {user_id}: {e}", exc_info=True)
            return []
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark an in-app notification as read."""
        logger.info(f"Marking notification {notification_id} as read for user {user_id}")
        try:
            # Update in memory
            notifications = InAppNotificationStore.get_user_notifications(user_id)
            for notif in notifications:
                if hasattr(notif, 'id') and notif.id == notification_id:
                    notif.read = True
            # Update in database
            if self.db:
                notif = self.db.query(Notification).filter(
                    Notification.id == notification_id,
                    Notification.user_id == user_id,
                    Notification.notif_type == "in_app"
                ).first()
                if notif:
                    notif.read = True
                    self.db.commit()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error marking notification {notification_id} as read for user {user_id}: {e}", exc_info=True)
            return False
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all in-app notifications as read for a user."""
        logger.info(f"Marking all notifications as read for user {user_id}")
        try:
            if not self.db:
                return 0
            count = self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.notif_type == "in_app",
                Notification.read == False
            ).update({"read": True})
            self.db.commit()
            # Update in-memory store
            notifications = InAppNotificationStore.get_user_notifications(user_id)
            for notif in notifications:
                notif.read = True
            return count
        except Exception as e:
            logger.error(f"Error marking all notifications as read for user {user_id}: {e}", exc_info=True)
            return 0
    
    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """Delete an in-app notification."""
        logger.info(f"Deleting notification {notification_id} for user {user_id}")
        try:
            if not self.db:
                return False
            notif = self.db.query(Notification).filter(
                Notification.id == notification_id,
                Notification.user_id == user_id,
                Notification.notif_type == "in_app"
            ).first()
            if notif:
                self.db.delete(notif)
                self.db.commit()
                # Remove from in-memory store
                notifications = InAppNotificationStore._notifications
                InAppNotificationStore._notifications = [
                    n for n in notifications 
                    if not (hasattr(n, 'id') and n.id == notification_id and n.user_id == user_id)
                ]
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting notification {notification_id} for user {user_id}: {e}", exc_info=True)
            return False
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread in-app notifications."""
        logger.info(f"Getting unread notification count for user {user_id}")
        try:
            if not self.db:
                # Count from in-memory store
                notifications = InAppNotificationStore.get_user_notifications(user_id)
                return len([n for n in notifications if not n.read])
            return self.db.query(Notification).filter(
                Notification.user_id == user_id,
                Notification.notif_type == "in_app",
                Notification.read == False
            ).count()
        except Exception as e:
            logger.error(f"Error getting unread count for user {user_id}: {e}", exc_info=True)
            return 0
    
    # Helper methods
    def _get_user_email(self, user_id: int) -> str:
        """Get user email from database."""
        try:
            if self.db:
                user = self.db.query(User).filter(User.id == user_id).first()
                if user and hasattr(user, 'email'):
                    return user.email
            # Fallback
            return f"user{user_id}@example.com"
        except Exception as e:
            logger.error(f"Error getting email for user {user_id}: {e}", exc_info=True)
            return f"user{user_id}@example.com"


# Backward compatibility functions (for your existing handler)
# def get_user_preferences(user_id: int, db: Session = None) -> dict:
#     """
#     Fetch user notification preferences (backward compatible).
#     """
#     service = NotificationService(db=db)
#     return service.get_user_preferences(user_id)


# def process_notification_event(event: dict, db: Session = None):
#     """
#     Process notification event (backward compatible).
#     """
#     service = NotificationService(db=db)
#     return service.process_notification_event(event)


# def send_email_notification(user_id: int, message: str, to_email: str = None, db: Session = None):
#     """
#     Send email notification (backward compatible).
#     """
#     service = NotificationService(db=db)
#     return service.send_email_notification(user_id, message, to_email)


# def send_in_app_notification(user_id: int, message: str, db: Session = None):
#     """
#     Send in-app notification (backward compatible).
#     """
#     service = NotificationService(db=db)
#     return service.send_in_app_notification(user_id, message)