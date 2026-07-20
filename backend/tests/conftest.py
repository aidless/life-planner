"""Pytest conftest - shared fixtures and path setup."""

import sys
from pathlib import Path

import pytest

# Make the backend/ directory importable so `import app.main` works
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def clear_rate_limiter() -> None:
    """Wipe the in-memory rate limiter. Best-effort: not finding it is fine."""
    try:
        from app.main import app
        # Force the middleware stack to be built (it's lazy)
        from fastapi.testclient import TestClient
        TestClient(app).get("/api/health")

        # Walk app.user_middleware (list of Starlette Middleware objects)
        # and find the live RateLimitMiddleware instance.
        for mw in app.user_middleware:
            cls = mw.cls
            if cls and getattr(cls, "__name__", "") == "RateLimitMiddleware":
                # user_middleware stores CL options; the live instance
                # is built during app startup. We can find it via the
                # running app stack.
                pass
        # Best-effort: try the live stack
        try:
            stack = app.middleware_stack
            if stack is not None:
                for m_attr in dir(stack):
                    m_obj = getattr(stack, m_attr, None)
                    if m_obj and getattr(m_obj, "request_counts", None) is not None:
                        m_obj.request_counts.clear()
                        return
        except Exception:
            pass
    except Exception:
        # Never let the fixture break tests
        pass


@pytest.fixture(autouse=True)
def _reset_state():
    """Run before every test: clear rate-limit state."""
    clear_rate_limiter()
    yield
