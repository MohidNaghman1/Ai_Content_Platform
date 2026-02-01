# Notification models
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from ai_content_platform.app.database import Base

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    message = Column(String, nullable=False)
    notif_type = Column(String, nullable=False)  # 'email' or 'in_app'
    read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class InAppNotificationStore:
    """
    Simulated in-app notification storage (in-memory for demo).
    """
    _notifications = []

    @classmethod
    def add_notification(cls, notification):
        cls._notifications.append(notification)

    @classmethod
    def get_user_notifications(cls, user_id: int):
        return [n for n in cls._notifications if n.user_id == user_id]
