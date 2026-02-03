from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from ai_content_platform.app.modules.notifications.services import NotificationService
from ai_content_platform.app.events.publishers import publish_event
from ai_content_platform.app.shared.dependencies import get_db
from ai_content_platform.app.modules.notifications.schemas import (
    NotificationCreate,
    NotificationResponse,
    MarkReadRequest,
)
from typing import List
from datetime import datetime
from ai_content_platform.app.shared.logging import get_logger
from ai_content_platform.app.shared.dependencies import require_permission

logger = get_logger(__name__)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


@router.post(
    "/send",
    status_code=201,
    dependencies=[Depends(require_permission("send_notifications"))],
    summary="N1: Send Notification",
    description="""
    **N1: Send Notification**\n
    Queue a notification for a user. Publishes an event to the notification system, which will deliver via email, in-app, or both, depending on the `type` and user preferences.\n
    - **user_id**: ID of the user to send notification to\n    - **message**: Notification message content\n    - **type**: Type of notification (\"email\", \"in_app\", or \"notification\" for both)\n    - **email**: Optional email address (will fetch from DB if not provided)
    """,
)
def send_notification(notification: NotificationCreate):
    logger.info(
        f"API: Sending notification to user {notification.user_id} of type {notification.type}"
    )
    try:
        publish_event(
            stream_name="notifications",
            event_type=notification.type,
            payload={
                "user_id": notification.user_id,
                "message": notification.message,
                "email": notification.email,
            },
        )
        return {
            "success": True,
            "message": f"Notification queued for user {notification.user_id}",
            "type": notification.type,
        }
    except Exception as e:
        logger.error(f"API: Failed to send notification: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to send notification: {str(e)}"
        )


@router.get(
    "/{user_id}",
    response_model=List[NotificationResponse],
    dependencies=[Depends(require_permission("view_notifications"))],
    summary="N2: Get User Notifications",
    description="""
    **N2: Get User Notifications**\n
    Retrieve a list of in-app notifications for a specific user. Supports filtering for unread notifications and limiting the number of results.\n
    - **user_id**: ID of the user\n    - **unread_only**: If true, returns only unread notifications\n    - **limit**: Maximum number of notifications to return (max 100)
    """,
)
def get_user_notifications(
    user_id: int,
    unread_only: bool = Query(False, description="Filter only unread notifications"),
    limit: int = Query(
        50, le=100, description="Maximum number of notifications to return"
    ),
    db: Session = Depends(get_db),
):
    """
    Get in-app notifications for a specific user.

    - **user_id**: ID of the user
    - **unread_only**: If true, returns only unread notifications
    - **limit**: Maximum number of notifications to return (max 100)
    """
    logger.info(
        f"API: Fetching notifications for user {user_id}, unread_only={unread_only}, limit={limit}"
    )
    try:
        service = NotificationService(db=db)
        notifications = service.get_user_notifications(user_id, unread_only, limit)
        return notifications
    except Exception as e:
        logger.error(
            f"API: Error fetching notifications for user {user_id}: {e}", exc_info=True
        )
        raise HTTPException(500, f"Failed to fetch notifications for user {user_id}")


@router.get(
    "/{user_id}/unread-count",
    dependencies=[Depends(require_permission("view_notifications"))],
    summary="N3: Get Unread Notification Count",
    description="""
    **N3: Get Unread Notification Count**\n
    Get the count of unread in-app notifications for a user.\n
    - **user_id**: ID of the user
    """,
)
def get_unread_count(user_id: int, db: Session = Depends(get_db)):
    """
    Get the count of unread in-app notifications for a user.

    - **user_id**: ID of the user
    """
    logger.info(f"API: Fetching unread notification count for user {user_id}")
    try:
        service = NotificationService(db=db)
        count = service.get_unread_count(user_id)
        return {"user_id": user_id, "unread_count": count}
    except Exception as e:
        logger.error(
            f"API: Error fetching unread count for user {user_id}: {e}", exc_info=True
        )
        raise HTTPException(500, f"Failed to fetch unread count for user {user_id}")


@router.patch(
    "/{notification_id}/read",
    dependencies=[Depends(require_permission("view_notifications"))],
    summary="N4: Mark Notification as Read",
    description="""
    **N4: Mark Notification as Read**\n
    Mark a specific notification as read for a user.\n
    - **notification_id**: ID of the notification to mark as read\n    - **user_id**: ID of the user (for authorization)
    """,
)
def mark_notification_as_read(
    notification_id: int, request: MarkReadRequest, db: Session = Depends(get_db)
):
    """
    Mark a specific notification as read.

    - **notification_id**: ID of the notification to mark as read
    - **user_id**: ID of the user (for authorization)
    """
    logger.info(
        f"API: Marking notification {notification_id} as read for user {request.user_id}"
    )
    try:
        service = NotificationService(db=db)
        success = service.mark_as_read(notification_id, request.user_id)
        if not success:
            logger.warning(
                f"API: Notification {notification_id} not found for user {request.user_id}"
            )
            raise HTTPException(
                status_code=404,
                detail=f"Notification {notification_id} not found for user {request.user_id}",
            )
        return {
            "success": True,
            "notification_id": notification_id,
            "message": "Notification marked as read",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"API: Error marking notification {notification_id} as read: {e}",
            exc_info=True,
        )
        raise HTTPException(500, f"Failed to mark notification as read")


@router.patch(
    "/{user_id}/read-all",
    dependencies=[Depends(require_permission("view_notifications"))],
    summary="N5: Mark All Notifications as Read",
    description="""
    **N5: Mark All Notifications as Read**\n
    Mark all in-app notifications as read for a user.\n
    - **user_id**: ID of the user
    """,
)
def mark_all_notifications_as_read(user_id: int, db: Session = Depends(get_db)):
    """
    Mark all in-app notifications as read for a user.

    - **user_id**: ID of the user
    """
    logger.info(f"API: Marking all notifications as read for user {user_id}")
    try:
        service = NotificationService(db=db)
        count = service.mark_all_as_read(user_id)
        return {
            "success": True,
            "user_id": user_id,
            "marked_read": count,
            "message": f"Marked {count} notifications as read",
        }
    except Exception as e:
        logger.error(
            f"API: Error marking all notifications as read for user {user_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(500, f"Failed to mark all notifications as read")


@router.delete(
    "/{notification_id}",
    dependencies=[Depends(require_permission("view_notifications"))],
    summary="N6: Delete Notification",
    description="""
    **N6: Delete Notification**\n
    Delete a specific notification for a user.\n
    - **notification_id**: ID of the notification to delete\n    - **user_id**: ID of the user (for authorization)
    """,
)
def delete_notification(
    notification_id: int,
    user_id: int = Query(..., description="User ID for authorization"),
    db: Session = Depends(get_db),
):
    """
    Delete a specific notification.

    - **notification_id**: ID of the notification to delete
    - **user_id**: ID of the user (for authorization)
    """
    logger.info(f"API: Deleting notification {notification_id} for user {user_id}")
    try:
        service = NotificationService(db=db)
        success = service.delete_notification(notification_id, user_id)
        if not success:
            logger.warning(
                f"API: Notification {notification_id} not found for user {user_id}"
            )
            raise HTTPException(
                status_code=404,
                detail=f"Notification {notification_id} not found for user {user_id}",
            )
        return {
            "success": True,
            "notification_id": notification_id,
            "message": "Notification deleted successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"API: Error deleting notification {notification_id} for user {user_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(500, f"Failed to delete notification")


@router.get(
    "/{user_id}/preferences",
    dependencies=[Depends(require_permission("view_notifications"))],
    summary="N7: Get User Notification Preferences",
    description="""
    **N7: Get User Notification Preferences**\n
    Retrieve the notification channel preferences (email/in-app) for a user.\n
    - **user_id**: ID of the user
    """,
)
def get_user_notification_preferences(user_id: int, db: Session = Depends(get_db)):
    """
    Get notification preferences for a user.

    - **user_id**: ID of the user
    """
    logger.info(f"API: Fetching notification preferences for user {user_id}")
    try:
        service = NotificationService(db=db)
        preferences = service.get_user_preferences(user_id)
        return {"user_id": user_id, "preferences": preferences}
    except Exception as e:
        logger.error(
            f"API: Error fetching notification preferences for user {user_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(500, f"Failed to fetch notification preferences")


# ========== Health Check ==========


@router.get(
    "/health",
    summary="N8: Notification Service Health Check",
    description="""
    **N8: Notification Service Health Check**\n
    Check if the notification service is running and healthy.
    """,
)
def health_check():
    logger.info("API: Health check called for notifications service")
    return {
        "status": "healthy",
        "service": "notifications",
        "timestamp": datetime.utcnow().isoformat(),
    }
