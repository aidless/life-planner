"""Application configuration loaded from environment variables."""

import os
from functools import lru_cache
from typing import List


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
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"),
    )

    # AI
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    # claude-sonnet-4-6 为 Anthropic 当前有效 dateless 型号（liteLLM provider 清单核实，
    # 2026-09；dateless 别名始终指向该代最新快照）。设置 key 后自动生效。
    AI_MODEL: str = os.getenv("AI_MODEL", "claude-sonnet-4-6")

    # CORS
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173"
    ).split(",")


@lru_cache()
def get_settings() -> Settings:
    """Singleton settings accessor (cached)."""
    return Settings()
