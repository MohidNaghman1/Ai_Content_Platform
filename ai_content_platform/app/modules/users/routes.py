"""
User API routes: registration, profile, update, avatar upload.
All endpoints use async SQLAlchemy and Pydantic schemas.
"""

from fastapi import APIRouter, Depends, HTTPException
from ai_content_platform.app.shared.dependencies import (
    get_current_user,
    get_db,
    require_permission,
)
from ai_content_platform.app.modules.users.schemas import (
    UserCreate,
    UserOut,
    UserUpdate,
)
from ai_content_platform.app.modules.users.services import (
    create_user,
    get_user_by_username,
    get_password_hash,
)
from ai_content_platform.app.modules.users.models import User
from ai_content_platform.app.modules.users.schemas import UserOut
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from ai_content_platform.app.shared.logging import get_logger

logger = get_logger(__name__)

user_router = APIRouter(prefix="/users", tags=["users"])

# Example: List all users (requires 'view_users' permission)


@user_router.get(
    "/",
    response_model=list[UserOut],
    dependencies=[Depends(require_permission("view_users"))],
)
async def list_users_endpoint(db: AsyncSession = Depends(get_db)):
    logger.info("API: Listing all users")
    try:
        result = await db.execute(select(User))
        users = result.scalars().all()
        return [UserOut.model_validate(u) for u in users]
    except Exception as e:
        logger.error(f"API: Error listing users: {e}", exc_info=True)
        raise HTTPException(500, "Failed to list users")


# Get current user's profile


@user_router.get("/me", response_model=UserOut)
async def get_profile(
    current_user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    logger.info(f"API: Fetching profile for user {current_user.username}")
    try:
        user = await get_user_by_username(db, current_user.username)
        if not user:
            logger.warning(f"API: User not found: {current_user.username}")
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"API: Error fetching profile for user {current_user.username}: {e}",
            exc_info=True,
        )
        raise HTTPException(500, "Failed to fetch user profile")


# Update current user's profile


@user_router.put("/me", response_model=UserOut)
async def update_profile(
    update: UserUpdate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's profile."""
    logger.info(f"API: Updating profile for user {current_user.username}")
    try:
        # Fetch the user model from DB
        user = await get_user_by_username(db, current_user.username)
        if not user:
            logger.warning(f"API: User not found for update: {current_user.username}")
            raise HTTPException(status_code=404, detail="User not found")
        if update.username:
            user.username = update.username
        if update.password:
            user.hashed_password = get_password_hash(update.password)
        if update.avatar:
            user.avatar = update.avatar
        if update.email:
            user.email = update.email
        await db.commit()
        await db.refresh(user)
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"API: Error updating profile for user {current_user.username}: {e}",
            exc_info=True,
        )
        raise HTTPException(500, "Failed to update user profile")


# create user
@user_router.post("/", response_model=UserOut)
async def create_user_endpoint(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create a new user."""
    logger.info(f"API: Creating user {user_in.username}")
    try:
        user = await create_user(db, user_in)
        return user
    except Exception as e:
        logger.error(f"API: Error creating user {user_in.username}: {e}", exc_info=True)
        raise HTTPException(500, "Failed to create user")


# Upload avatar (simple string path, for demo)


@user_router.post("/me/avatar", response_model=UserOut)
async def upload_avatar(
    avatar: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update the current user's avatar (string path)."""
    logger.info(f"API: Uploading avatar for user {current_user.username}")
    try:
        user = await get_user_by_username(db, current_user.username)
        if not user:
            logger.warning(
                f"API: User not found for avatar upload: {current_user.username}"
            )
            raise HTTPException(status_code=404, detail="User not found")
        user.avatar = avatar
        await db.commit()
        await db.refresh(user)
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"API: Error uploading avatar for user {current_user.username}: {e}",
            exc_info=True,
        )
        raise HTTPException(500, "Failed to upload avatar")
