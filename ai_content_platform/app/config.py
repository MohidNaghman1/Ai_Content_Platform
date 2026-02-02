"""
App configuration using Pydantic BaseSettings.
Loads environment variables for DB and secret settings.
"""

from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    """
    Settings class for application configuration.
    Loads DB and secret settings from environment variables or .env file.
    """

    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 5432))
    DB_NAME: str = os.getenv("DB_NAME", "ai_content_platform")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your_secret_key")
    Gemini_API_KEY: str = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")


settings = Settings()
