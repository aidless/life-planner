"""Application configuration loaded from environment variables."""

import os
import secrets
from functools import lru_cache
from typing import List


def _jwt_secret() -> str:
    """Use SECRET_KEY or the legacy JWT_SECRET_KEY; never sign with empty."""

    configured = os.getenv("SECRET_KEY") or os.getenv("JWT_SECRET_KEY")
    if configured:
        return configured
    # Local/demo fallback. Tokens do not survive a restart, but no one can
    # forge them with an empty key. Production should set SECRET_KEY.
    return secrets.token_urlsafe(48)


class Settings:
    """Application settings with sensible defaults for development."""

    APP_NAME: str = "人生规划系统 (Life Planner)"
    VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./life_planner.db",
    )

    # Authentication
    SECRET_KEY: str = _jwt_secret()
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"),
    )

    # AI
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "claude-sonnet-4-6")

    # CORS
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173"
    ).split(",")


@lru_cache()
def get_settings() -> Settings:
    """Singleton settings accessor (cached)."""
    return Settings()
