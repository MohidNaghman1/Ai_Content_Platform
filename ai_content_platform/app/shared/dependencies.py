"""
Shared FastAPI dependencies for authentication, RBAC, and DB session management.
Includes JWT token validation, role-based access, and async DB session dependency.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ai_content_platform.app.shared.utils import verify_access_token
from ai_content_platform.app.modules.auth.models import Role
from ai_content_platform.app.database import AsyncSessionLocal
from ai_content_platform.app.modules.users.models import User
from ai_content_platform.app.shared.logging import get_logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

logger = get_logger(__name__)


# Set tokenUrl to /auth/login so Swagger UI Authorize button works correctly
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# Database session dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    Dependency to extract and validate the current user from a JWT token.
    Fetches the user from the DB with roles and permissions.
    """
    logger.info("Extracting current user from JWT token.")
    try:
        payload = verify_access_token(token)
        if payload is None:
            logger.warning("Invalid JWT token: could not validate credentials.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        username = payload.get("sub")
        if not username:
            logger.warning("JWT token missing subject (sub) claim.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
            )
        result = await db.execute(
            select(User)
            .where(User.username == username)
            .options(selectinload(User.roles).selectinload(Role.permissions))
        )
        user = result.scalars().first()
        if not user:
            logger.warning(f"User not found for username: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        logger.info(f"Authenticated user: {username}")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error extracting current user: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to extract current user")


# RBAC: Get user permissions from roles


async def get_user_permissions(current_user: User = Depends(get_current_user)):
    logger.info(
        f"Fetching permissions for user: {getattr(current_user, 'username', None)}"
    )
    try:
        permissions = set()
        if hasattr(current_user, "roles"):
            for role in current_user.roles:
                for perm in getattr(role, "permissions", []):
                    permissions.add(perm.name)
        return permissions
    except Exception as e:
        logger.error(f"Error fetching user permissions: {e}", exc_info=True)
        return set()


# RBAC: Require a specific permission


def require_permission(permission: str):
    def _log_permission_check(user, has_permission):
        username = getattr(user, "username", None)
        if has_permission:
            logger.info(f"Permission '{permission}' granted for user: {username}")
        else:
            logger.warning(f"Permission '{permission}' denied for user: {username}")

    async def permission_checker(current_user: User = Depends(get_current_user)):
        try:
            user_permissions = await get_user_permissions(current_user)
            if permission not in user_permissions:
                _log_permission_check(current_user, False)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
                )
            _log_permission_check(current_user, True)
            return current_user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Error checking permission '{permission}': {e}", exc_info=True
            )
            raise HTTPException(500, f"Failed to check permission '{permission}'")

    return permission_checker


def require_role(required_role: str):
    async def role_dependency(user: User = Depends(get_current_user)):
        try:
            if getattr(user, "role", None) != required_role:
                logger.warning(
                    f"Role '{required_role}' required, but user has role '{getattr(user, 'role', None)}'"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Insufficient privileges: requires {required_role}",
                )
            logger.info(
                f"Role '{required_role}' granted for user: {getattr(user, 'username', None)}"
            )
            return user
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error checking role '{required_role}': {e}", exc_info=True)
            raise HTTPException(500, f"Failed to check role '{required_role}'")

    return role_dependency
