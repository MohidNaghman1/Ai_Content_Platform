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
from ai_content_platform.app.modules.users.models import user_roles

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


async def create_user(db: AsyncSession, user_data):
    """
    Create a user using user_data dict/object with keys: username, email, password, role.
    Inserts user, flushes for constraints, fetches role, assigns, commits, and rolls back on error.
    """
    logger.info(
        f"Creating user: {getattr(user_data, 'username', None) or user_data.get('username')}"
    )
    try:
        # Hash password
        password = (
            user_data["password"] if isinstance(user_data, dict) else user_data.password
        )
        hashed_password = get_password_hash(password)

        # Create user instance (without roles yet)
        user = User(
            username=(
                user_data["username"]
                if isinstance(user_data, dict)
                else user_data.username
            ),
            email=(
                user_data["email"] if isinstance(user_data, dict) else user_data.email
            ),
            hashed_password=hashed_password)
        
        db.add(user)
        try:
            await db.flush()  # user.id available
        except Exception as e:
            await db.rollback()
            logger.error(f"Error during flush: {e}", exc_info=True)
            raise

        # Fetch the Role object from the DB
        role_name = user_data["role"] if isinstance(user_data, dict) else user_data.role
        result = await db.execute(select(Role).where(Role.name == role_name))
        role_obj = result.scalar_one_or_none()
        if not role_obj:
            await db.rollback()
            logger.error(f"Role '{role_name}' does not exist.")
            raise ValueError(f"Role '{role_name}' does not exist.")

        # Assign role via association table (user_roles)
        await db.execute(
            user_roles.insert().values(
                user_id=user.id,
                role_id=role_obj.id,
            )
        )

        await db.commit()
        await db.refresh(user)

        # Trigger notification event (example: welcome message)
        try:
            publish_event(
                stream_name="notifications",
                event_type="USER_REGISTERED",
                payload={"user_id": user.id, "message": f"Welcome, {user.username}!"},
            )
            logger.info(f"Published USER_REGISTERED event for user {user.id}")
        except Exception as e:
            logger.error(
                f"Error publishing USER_REGISTERED event for user {user.id}: {e}",
                exc_info=True,
            )
        return user
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating user: {e}", exc_info=True)
        raise
