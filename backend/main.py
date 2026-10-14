"""DEPRECATED entry point — do not use.

Canonical entry is backend/app/main.py (19 routers, referenced by
README/QUICKSTART as ``app.main:app``). This file is kept only so old
imports fail loudly instead of silently serving a stale 4-router app.
It will be removed after 2026-12-31.
"""
import warnings

warnings.warn(
    "backend.main is deprecated; use backend.app.main (app.main:app) instead. "
    "This shim will be removed after 2026-12-31.",
    DeprecationWarning,
    stacklevel=2,
)

from backend.app.main import app  # noqa: F401  (canonical app, 19 routers)
