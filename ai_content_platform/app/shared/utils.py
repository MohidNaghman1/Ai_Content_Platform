"""
JWT and Auth Utilities
Provides functions for creating and verifying JWT tokens using environment-based secrets.
"""

import secrets
import os
import redis
from dotenv import load_dotenv
from fastapi import HTTPException, status
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timedelta
from ai_content_platform.app.shared.logging import get_logger

logger = get_logger(__name__)


# Load environment variables
load_dotenv(
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env")
)

# Redis connection utility


def get_redis_connection():
    try:
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        logger.info(f"Connecting to Redis at {redis_url}")
        conn = redis.Redis.from_url(redis_url, decode_responses=True)
        logger.info("Redis connection established.")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to Redis: {e}", exc_info=True)
        raise


SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create a JWT access token for the given data.
    Optionally set a custom expiration delta.
    """
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        logger.info(f"Access token created for subject: {data.get('sub', 'unknown')}")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Error creating access token: {e}", exc_info=True)
        raise


def verify_access_token(token: str):
    """
    Verify a JWT access token and return the payload if valid.
    Returns None if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.warning("Invalid token: missing subject (sub)")
            return HTTPException(
                status_code=401, detail="Invalid token: missing subject"
            )
        logger.info(f"Access token verified for subject: {username}")
        return payload
    except JWTError as e:
        logger.warning(f"Token expired or invalid: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"Error verifying access token: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_refresh_token():
    """
    Create a secure random refresh token.
    """
    try:
        token = secrets.token_urlsafe(32)
        logger.info("Refresh token created.")
        return token
    except Exception as e:
        logger.error(f"Error creating refresh token: {e}", exc_info=True)
        raise
