"""Pytest conftest - shared fixtures and path setup.

P6: 测试库隔离 —— 在任何 app 导入之前把 DATABASE_URL 指向独立测试库，
pytest 全程不再触碰正式库（之前跑一次留 35 测试号，封存前被迫清库）。
"""

import os
import sys
from pathlib import Path

import pytest

# Make the backend/ directory importable so `import app.main` works
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# P6: 绝对路径独立测试库（*.db 已在 .gitignore，不进仓库）。
# 必须在首次 `import app.*` 之前设置，因为 engine/settings 是模块级单例。
# 用绝对路径：sqlite 相对路径随 cwd 解析（仓库根 vs backend/ 各有一个
# life_planner.db，以前两种都被污染过）。
# P6: 异步兼容式 URL（legacy database.py 用 create_async_engine，
# 要求 +aiosqlite 驱动；同步侧各自 strip，见 app/database.py）。
os.environ["DATABASE_URL"] = (
    f"sqlite+aiosqlite:///{BACKEND_DIR / 'tests' / 'test_isolated.db'}"
)


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
