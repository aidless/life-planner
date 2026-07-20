"""
Database configuration and session management.
Uses SQLAlchemy 2.0 async mode with SQLite (dev) / PostgreSQL (prod).
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from typing import AsyncGenerator, Generator
import logging

from config import settings

logger = logging.getLogger(__name__)

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    future=True,
)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create sync engine (for scripts/migrations)
sync_engine = create_engine(
    settings.DATABASE_URL.replace("+aiosqlite", ""),
    echo=settings.DATABASE_ECHO,
)

# Create sync session maker (for seed data scripts)
SyncSessionLocal = sessionmaker(
    sync_engine,
    autocommit=False,
    autoflush=False,
)

# Create declarative base for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency injection for database session.
    Yields an async database session and closes it after use.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_db():
    """
    Initialize database tables.
    Creates all tables defined in models.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")


async def close_db():
    """
    Close database engine.
    Should be called on application shutdown.
    """
    await engine.dispose()
    logger.info("Database engine disposed")
