"""
Authentication service functions for login.
Uses real database for user lookup and password verification.
"""

from ai_content_platform.app.shared.logging import get_logger
from sqlalchemy.ext.asyncio import AsyncSession
from ai_content_platform.app.modules.users.services import (
    get_user_by_username,
    verify_password,
)
import hashlib
from datetime import datetime, timedelta
from sqlalchemy import select, update
from ai_content_platform.app.modules.auth.models import RefreshToken
from ai_content_platform.app.shared.utils import (
    create_access_token,
    create_refresh_token,
)

logger = get_logger(__name__)

REFRESH_TOKEN_EXPIRE_DAYS = 7  # Or import from config


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


async def authenticate_user(username: str, password: str, db: AsyncSession = None):
    """
    Asynchronously authenticate a user by username and password using the database.
    Returns user object (with .username, .role, .hashed_password) or None.
    """
    try:
        if db is None:
            logger.error("Database session is required for authentication.")
            raise ValueError("Database session is required for authentication.")
        user = await get_user_by_username(db, username)
        if not user or not verify_password(password, user.hashed_password):
            logger.warning(f"Failed authentication for user: {username}")
            return None
        logger.info(f"User authenticated: {username}")
        return user
    except Exception as e:
        logger.error(f"Error authenticating user {username}: {e}", exc_info=True)
        raise


async def issue_tokens(user, db):
    try:
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role},
            expires_delta=timedelta(minutes=30),
        )
        refresh_token = create_refresh_token()
        db_refresh = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )
        db.add(db_refresh)
        await db.commit()
        logger.info(f"Issued tokens for user: {user.username}")
        return access_token, refresh_token
    except Exception as e:
        logger.error(
            f"Error issuing tokens for user {getattr(user, 'username', None)}: {e}",
            exc_info=True,
        )
        raise


async def rotate_refresh_token(refresh_token, db, User):
    try:
        token_hash_val = hash_token(refresh_token)
        db_token = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash_val, RefreshToken.revoked == False
            )
        )
        db_token = db_token.scalar_one_or_none()
        if not db_token or db_token.expires_at < datetime.utcnow():
            logger.warning("Invalid or expired refresh token during rotation.")
            return None, None, None
        user = await db.get(User, db_token.user_id)
        db_token.revoked = True
        new_refresh_token = create_refresh_token()
        new_db_token = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(new_refresh_token),
            expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )
        db.add(new_db_token)
        await db.commit()
        new_access_token = create_access_token(
            data={"sub": user.username, "role": user.role},
            expires_delta=timedelta(minutes=30),
        )
        logger.info(f"Rotated refresh token for user: {user.username}")
        return new_access_token, new_refresh_token, user
    except Exception as e:
        logger.error(f"Error rotating refresh token: {e}", exc_info=True)
        raise


async def revoke_refresh_token(refresh_token, db):
    try:
        token_hash_val = hash_token(refresh_token)
        result = await db.execute(
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash_val)
            .values(revoked=True)
        )
        await db.commit()
        logger.info(f"Revoked refresh token: {refresh_token}")
        return result.rowcount
    except Exception as e:
        logger.error(f"Error revoking refresh token: {e}", exc_info=True)
        raise
