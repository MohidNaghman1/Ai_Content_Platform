
"""
User service functions: hashing, DB queries, creation.
All business logic for user management.
"""
from sqlalchemy.ext.asyncio import AsyncSession
from ai_content_platform.app.events.publishers import publish_event
from sqlalchemy.future import select
from ai_content_platform.app.modules.users.models import User
from passlib.context import CryptContext
from ai_content_platform.app.modules.auth.models import Role
from ai_content_platform.app.shared.logging import get_logger
logger = get_logger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a plain password using bcrypt."""
    try:
        hashed = pwd_context.hash(password)
        logger.info("Password hashed successfully.")
        return hashed
    except Exception as e:
        logger.error(f"Error hashing password: {e}", exc_info=True)
        raise


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hash."""
    try:
        result = pwd_context.verify(plain_password, hashed_password)
        logger.info("Password verification attempted.")
        return result
    except Exception as e:
        logger.error(f"Error verifying password: {e}", exc_info=True)
        return False


async def get_user_by_username(db: AsyncSession, username: str):
    """Fetch a user by username from the DB."""
    logger.info(f"Fetching user by username: {username}")
    try:
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        return user
    except Exception as e:
        logger.error(f"Error fetching user by username {username}: {e}", exc_info=True)
        return None



async def create_user(
    db: AsyncSession,
    username: str,
    email: str,
    password: str,
    role: str
):
    logger.info(f"Creating user: {username}")
    try:
        hashed_password = get_password_hash(password)
        # Fetch the Role object from the DB
        result = await db.execute(select(Role).where(Role.name == role))
        role_obj = result.scalars().first()
        if not role_obj:
            logger.warning(f"Role '{role}' does not exist.")
            raise ValueError(f"Role '{role}' does not exist.")
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            role=role,
            roles=[role_obj],  # assign the many-to-many relationship
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        # Trigger notification event (example: welcome message)
        try:
            publish_event(
                stream_name="notifications",
                event_type="USER_REGISTERED",
                payload={"user_id": user.id, "message": f"Welcome, {user.username}!"}
            )
            logger.info(f"Published USER_REGISTERED event for user {user.id}")
        except Exception as e:
            logger.error(f"Error publishing USER_REGISTERED event for user {user.id}: {e}", exc_info=True)
        return user
    except Exception as e:
        logger.error(f"Error creating user {username}: {e}", exc_info=True)
        raise

