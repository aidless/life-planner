"""Alembic environment configuration (P7-B1 reworked).

P7-B1  honest state:
- 001 is a legacy-schema snapshot (old users/exams/exam_questions shapes);
  002 adds recommendation tables; 003_baseline_parity fills the ~29 app
  tables and rebuilds the 3 overlapping tables to the current (Base wins)
  shapes. Fresh DBs converge to create_all parity via `upgrade head`.
- This env must NOT execute side-effect engines at import. Legacy
  database.py creates an async engine at import time, so DATABASE_URL is
  normalized to an async form BEFORE any app/legacy import, and a separate
  sync engine is built here for the migration connection only.
- Production (port 4800) is NOT migrated by this file; it still boots via
  create_all. Existing prod DBs need a one-time `alembic stamp head` in a
  maintenance window — deliberately not done in B1.
"""

from logging.config import fileConfig
import os
import sys

from alembic import context
from sqlalchemy import create_engine, pool

# Add backend/ to path for imports (this file lives in backend/migrations/).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

RAW_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./life_planner.db")


def _to_async(url: str) -> str:
    if url.startswith("sqlite:") and "+aiosqlite" not in url:
        return url.replace("sqlite:", "sqlite+aiosqlite:", 1)
    return url


def _to_sync(url: str) -> str:
    # sqlite+aiosqlite:///... -> sqlite:///... ; leave postgres/python URLs alone
    if "+aiosqlite" in url:
        return url.replace("+aiosqlite", "")
    if "+" in url.split("://")[0]:
        scheme, rest = url.split("://", 1)
        return scheme.split("+")[0] + "://" + rest
    return url


# Normalize BEFORE importing anything that builds engines at import time
# (legacy database.py does create_async_engine at module top level).
os.environ["DATABASE_URL"] = _to_async(RAW_URL)
SYNC_URL = _to_sync(RAW_URL)

# Register all models: new app domains (Base wins on overlapping names)
# plus legacy models (legacy-only tables). No engine is executed here.
from app.modules.loader import discover as _discover  # noqa: E402

_discover()
import models  # noqa: E402,F401  (legacy tables onto database.Base)

from app.shared.base_model import Base as AppBase  # noqa: E402
from database import Base as LegacyBase  # noqa: E402

config = context.config
config.set_main_option("sqlalchemy.url", SYNC_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Both metadatas: autogenerate sees the union; overlapping names are
# resolved Base-first at runtime (create_all checkfirst skips existing).
target_metadata = [AppBase.metadata, LegacyBase.metadata]


def run_migrations_offline() -> None:
    context.configure(
        url=SYNC_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connect_args = {}
    if SYNC_URL.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    connectable = create_engine(SYNC_URL, poolclass=pool.NullPool, connect_args=connect_args)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
