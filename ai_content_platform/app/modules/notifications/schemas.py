from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class NotificationCreate(BaseModel):
    """Schema for creating a notification"""

    user_id: int
    message: str
    type: str = "notification"  # "email", "in_app", or "notification" (both)
    email: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 123,
                "message": "Your order has been shipped!",
                "type": "notification",
                "email": "user@example.com",
            }
        }
    )


class NotificationResponse(BaseModel):
    """Schema for notification response"""

    id: int
    user_id: int
    message: str
    notif_type: str
    read: bool
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 123,
                "message": "Your order has been shipped!",
                "notif_type": "in_app",
                "read": False,
                "created_at": "2024-01-29T10:30:00",
            }
        },
    )


class MarkReadRequest(BaseModel):
    """Schema for marking notification as read"""

    user_id: int
