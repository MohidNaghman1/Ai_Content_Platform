"""
SQLAlchemy User model.
Defines the users table for authentication and profile management.
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ai_content_platform.app.modules.auth.models import user_roles
from ai_content_platform.app.database import Base

from sqlalchemy import Boolean


class User(Base):
    """
    SQLAlchemy User model for authentication and user profile.
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="viewer", nullable=False)  # viewer, creator, admin
    avatar = Column(String, nullable=True)  # URL or file path to avatar
    # RBAC: relationship to roles
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    # Notification preferences
    email_notifications = Column(Boolean, default=True)
    in_app_notifications = Column(Boolean, default=True)
