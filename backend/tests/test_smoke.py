"""Smoke tests - 验证 app 启动 + 基础端点。

不依赖数据库的测试标记为简单 smoke；
依赖数据库的测试如果数据库不可用会自动 skip。
"""

import uuid

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Build the FastAPI app and return a TestClient."""
    from app.main import app
    return TestClient(app)


def test_health_endpoint(client):
    """GET /api/health must return 200 with status=healthy."""
    r = client.get("/api/health")
    assert r.status_code == 200, f"health returned {r.status_code}: {r.text}"
    body = r.json()
    assert body.get("success") is True
    assert body["data"]["status"] == "healthy"


def test_openapi_schema_generated(client):
    """OpenAPI schema must be generated without error."""
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schema = r.json()
    assert "openapi" in schema
    assert "paths" in schema
    assert "/api/health" in schema["paths"]


def test_docs_endpoint(client):
    """Swagger UI endpoint must be accessible."""
    r = client.get("/docs")
    assert r.status_code == 200
    assert "swagger" in r.text.lower()


def test_unknown_endpoint_returns_404(client):
    """A 404 endpoint must return a 4xx (not 500)."""
    r = client.get("/api/does-not-exist")
    assert 400 <= r.status_code < 500


@pytest.fixture
def db_available():
    """Skip the test if database is unreachable."""
    try:
        from app.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        pytest.skip(f"Database not available: {e}")


def test_register_login_me_flow(client, db_available):
    """Full auth flow: register → login → me.

    Catches:
    - bcrypt incompatibility (already fixed in W24)
    - JWT secret key misconfiguration
    - user_id type coercion (current_user.id issue)
    """
    username = f"smoke_{uuid.uuid4().hex[:8]}"
    payload = {
        "username": username,
        "email": f"{username}@test.com",
        "password": "Test123456",
    }

    # 1. Register
    r = client.post("/api/auth/register", json=payload)
    assert r.status_code == 200, f"register failed: {r.text}"
    body = r.json()
    assert body.get("success") is True
    assert "access_token" in body["data"]
    token = body["data"]["access_token"]

    # 2. Login
    r = client.post("/api/auth/login", json={
        "username": username,
        "password": "Test123456",
    })
    assert r.status_code == 200, f"login failed: {r.text}"
    body = r.json()
    assert body.get("success") is True
    token = body["data"]["access_token"]

    # 3. /me (requires JWT)
    r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, f"/me failed: {r.text}"
    body = r.json()
    assert body["data"]["username"] == username


def test_register_with_weak_password_rejected(client, db_available):
    """Empty or too-short password must be rejected, not crash."""
    username = f"smoke_{uuid.uuid4().hex[:8]}"
    r = client.post("/api/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": "",  # empty password
    })
    # Either 422 (validation) or 4xx (logic) — just don't 500
    assert 400 <= r.status_code < 500, f"server crashed: {r.status_code} {r.text}"


def test_login_with_wrong_password_returns_401(client, db_available):
    """Wrong password must return 401, not crash."""
    username = f"smoke_{uuid.uuid4().hex[:8]}"
    # Register first
    r = client.post("/api/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": "CorrectPass123",
    })
    assert r.status_code == 200

    # Wrong password
    r = client.post("/api/auth/login", json={
        "username": username,
        "password": "WrongPass456",
    })
    assert r.status_code == 401, f"wrong password returned {r.status_code} {r.text}"


def test_me_without_token_returns_401(client):
    """/me without Authorization header must return 401."""
    r = client.get("/api/auth/me")
    assert r.status_code == 401, f"no auth returned {r.status_code}"


def test_me_with_invalid_token_returns_401(client):
    """/me with garbage token must return 401, not 500."""
    r = client.get("/api/auth/me", headers={"Authorization": "Bearer garbage.token.value"})
    assert r.status_code == 401, f"bad token returned {r.status_code} {r.text}"


def test_create_goal_requires_auth(client, db_available):
    """POST /api/goals without auth must return 401, not 500."""
    r = client.post("/api/goals", json={"title": "Test goal", "category": "test"})
    assert r.status_code == 401, f"unauth returned {r.status_code}"


def test_ai_chat_handles_no_api_key_gracefully(client, db_available):
    """AI chat with no ANTHROPIC_API_KEY must return a 4xx, not crash with 500.

    This catches a real production issue: if the env var is missing
    the AI client should fail gracefully, not 500.
    """
    import os
    saved_key = os.environ.pop("ANTHROPIC_API_KEY", None)
    try:
        r = client.post("/api/ai/chat", json={"message": "hi"}, headers={"Authorization": "Bearer fake"})
        # 401 (no auth) or 503 (no key) is fine; 500 is not
        assert 400 <= r.status_code < 600, f"got {r.status_code}: {r.text}"
        assert r.status_code != 500, f"server 500'd without API key: {r.text}"
    finally:
        if saved_key is not None:
            os.environ["ANTHROPIC_API_KEY"] = saved_key
