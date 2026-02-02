"""
Authentication API router: registration, login, refresh, logout endpoints.
Handles user registration, JWT login, token refresh, and logout.
"""

from ai_content_platform.app.modules.users.models import User
from ai_content_platform.app.modules.users.services import (
    get_user_by_username,
    create_user,
)
from ai_content_platform.app.shared.dependencies import get_db
from ai_content_platform.app.modules.auth.services import (
    authenticate_user,
    issue_tokens,
    rotate_refresh_token,
    revoke_refresh_token,
)
from ai_content_platform.app.modules.users.schemas import UserCreate, UserOut
from ai_content_platform.app.modules.auth.models import RefreshToken
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from ai_content_platform.app.shared.logging import get_logger

logger = get_logger(__name__)


auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post("/register", response_model=UserOut)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user with username, password, and role."""
    logger.info(f"Register endpoint called for username: {user_in.username}")
    try:
        existing = await get_user_by_username(db, user_in.username)
        if existing:
            logger.error(f"Username already registered: {user_in.username}")
            raise HTTPException(status_code=400, detail="Username already registered")
        # Optionally, check for existing email here as well
        user = await create_user(db, user_in)
        logger.info(f"User registered: {user_in.username}")
        return user
    except Exception as e:
        logger.error(f"Error in register endpoint: {e}", exc_info=True)
        raise


@auth_router.post("/login")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    response: Response = None,
):
    """OAuth2 login endpoint. Returns JWT access token on valid credentials."""
    logger.info(f"Login endpoint called for username: {form_data.username}")
    try:
        user = await authenticate_user(form_data.username, form_data.password, db)
        if not user:
            logger.warning(f"Login failed for username: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token, refresh_token = await issue_tokens(user, db)
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
        )
        logger.info(f"Login successful for username: {form_data.username}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except Exception as e:
        logger.error(f"Error in login endpoint: {e}", exc_info=True)
        raise


@auth_router.post("/token/refresh")
async def refresh_token(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Accepts a refresh token and returns a new access token.
    For demo: expects 'refresh_token' in JSON body.
    """
    logger.info("Refresh token endpoint called")
    try:
        data = await request.json()
        refresh_token = data.get("refresh_token")
        if not refresh_token:
            logger.error("Missing refresh token in request body")
            raise HTTPException(400, "Missing refresh token")
        from ai_content_platform.app.modules.users.models import User

        new_access_token, new_refresh_token, user = await rotate_refresh_token(
            refresh_token, db, User
        )
        if not new_access_token:
            logger.warning("Invalid refresh token provided")
            raise HTTPException(401, "Invalid refresh token")
        logger.info(
            f"Refresh token successful for user: {getattr(user, 'username', None)}"
        )
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
    except Exception as e:
        logger.error(f"Error in refresh_token endpoint: {e}", exc_info=True)
        raise


@auth_router.post("/token/revoke")
async def revoke_token(request: Request, db: AsyncSession = Depends(get_db)):
    logger.info("Revoke token endpoint called")
    try:
        data = await request.json()
        refresh_token = data.get("refresh_token")
        if not refresh_token:
            logger.error("Missing refresh token in request body")
            raise HTTPException(400, "Missing refresh token")
        rowcount = await revoke_refresh_token(refresh_token, db)
        if rowcount == 0:
            logger.warning("Token not found for revocation")
            raise HTTPException(404, "Token not found")
        logger.info("Token revoked successfully")
        return {"detail": "Token revoked"}
    except Exception as e:
        logger.error(f"Error in revoke_token endpoint: {e}", exc_info=True)
        raise


@auth_router.post("/token")
async def token_with_json(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Accepts username and password in JSON body, returns JWT tokens.
    """
    logger.info("Token endpoint called with JSON body")
    try:
        data = await request.json()
        username = data.get("username")
        password = data.get("password")
        if not username or not password:
            logger.error("Missing username or password in request body")
            raise HTTPException(400, "Missing username or password")
        user = await authenticate_user(username, password, db)
        if not user:
            logger.warning(f"Token endpoint: login failed for username: {username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token, refresh_token = await issue_tokens(user, db)
        logger.info(f"Token endpoint: login successful for username: {username}")
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    except Exception as e:
        logger.error(f"Error in token_with_json endpoint: {e}", exc_info=True)
        raise
