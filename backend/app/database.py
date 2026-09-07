"""Database engine and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import get_settings

settings = get_settings()

# P6: 同步 engine 剥掉 +aiosqlite（legacy 侧 create_async_engine 要求异步式
# URL，DATABASE_URL 因此统一为 sqlite+aiosqlite 形式；默认无后缀时为 no-op）。
SYNC_DATABASE_URL = settings.DATABASE_URL.replace("+aiosqlite", "")

connect_args = {}
if "sqlite" in SYNC_DATABASE_URL:
    connect_args["check_same_thread"] = False

engine = create_engine(
    SYNC_DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
