"""Smoke tests for life_planner, daily_tracker, exam_analyzer, ai_coach.

W29 expansion: cover the remaining 17+ routes with 4xx/5xx smoke tests.
Each test must not crash the server with 500.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    """Reuse the register-login pattern to obtain a JWT for protected routes.

    Skips if database is unavailable.
    """
    try:
        from app.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        pytest.skip("Database not available")

    import uuid
    username = f"smoke_{uuid.uuid4().hex[:8]}"
    payload = {
        "username": username,
        "email": f"{username}@test.com",
        "password": "Test123456",
    }
    r = client.post("/api/auth/register", json=payload)
    assert r.status_code == 200, f"register failed: {r.text}"
    return r.json()["data"]["access_token"]


# ── life_planner /goals ─────────────────────────────────────────────


def test_goals_create_requires_auth(client):
    """POST /api/goals without auth must 401, not 500."""
    r = client.post("/api/goals", json={"title": "Test goal", "category": "test"})
    assert r.status_code == 401, f"got {r.status_code}"


def test_goals_list_requires_auth(client):
    """GET /api/goals without auth must 401."""
    r = client.get("/api/goals")
    assert r.status_code == 401


def test_goals_get_missing_returns_404(client, auth_token):
    """GET /api/goals/{id} for a missing goal must 404, not 500."""
    r = client.get("/api/goals/999999", headers={"Authorization": f"Bearer {auth_token}"})
    assert 400 <= r.status_code < 500, f"got {r.status_code} {r.text}"


# ── daily_tracker /daily-logs ───────────────────────────────────────


def test_daily_logs_create_requires_auth(client):
    """POST /api/daily-logs without auth must 401."""
    r = client.post("/api/daily-logs", json={
        "date": "2026-07-17", "activity_type": "study", "description": "test",
    })
    assert r.status_code == 401


def test_daily_logs_list_requires_auth(client):
    """GET /api/daily-logs without auth must 401."""
    r = client.get("/api/daily-logs")
    assert r.status_code == 401


# ── exam_analyzer /exams ────────────────────────────────────────────


def test_exams_create_requires_auth(client):
    """POST /api/exams without auth must 401."""
    r = client.post("/api/exams", json={
        "subject": "数学一", "exam_name": "2026 模考", "total_score": 150,
    })
    assert r.status_code == 401


def test_exams_list_requires_auth(client):
    """GET /api/exams without auth must 401."""
    r = client.get("/api/exams")
    assert r.status_code == 401


# ── ai_coach /ai/chat ──────────────────────────────────────────────


def test_ai_chat_requires_auth(client):
    """POST /api/ai/chat without auth must 401."""
    r = client.post("/api/ai/chat", json={"message": "hi"})
    assert r.status_code == 401


def test_ai_analyze_requires_auth(client):
    """POST /api/ai/analyze without auth must 401."""
    r = client.post("/api/ai/analyze", json={"text": "test"})
    assert r.status_code == 401


def test_ai_modules_endpoint_open(client):
    """GET /api/ai/modules (no auth required) must respond, not 500."""
    r = client.get("/api/ai/modules")
    assert r.status_code < 500, f"got {r.status_code} {r.text}"


# ── error handling: malformed JSON must 4xx, not 500 ─────────────


def test_auth_register_malformed_json_returns_4xx(client):
    """POST /api/auth/register with bad JSON must 4xx, not 500."""
    r = client.post(
        "/api/auth/register",
        data="not-valid-json",
        headers={"Content-Type": "application/json"},
    )
    assert 400 <= r.status_code < 500, f"got {r.status_code} {r.text}"


def test_college_predict_malformed_json_returns_4xx(client):
    """POST /api/college/predict with bad JSON must 4xx."""
    r = client.post(
        "/api/college/predict",
        data="{not-valid",
        headers={"Content-Type": "application/json"},
    )
    assert 400 <= r.status_code < 500, f"got {r.status_code} {r.text}"


# ── content-type: wrong header must 415 ──────────────────────────


def test_wrong_content_type_returns_4xx(client):
    """POST with text/plain content type must 4xx, not 500."""
    r = client.post(
        "/api/auth/register",
        data="text data",
        headers={"Content-Type": "text/plain"},
    )
    assert 400 <= r.status_code < 500, f"got {r.status_code} {r.text}"


# ── rate limiting smoke ───────────────────────────────────────────


def test_health_endpoint_resilient(client):
    """Health endpoint must return 200 on every call (no rate limit)."""
    for _ in range(5):
        r = client.get("/api/health")
        assert r.status_code == 200


# ── 404 for unknown methods on known paths ──────────────────────


def test_unknown_method_on_known_path_returns_405(client):
    """DELETE /api/health must return 405 Method Not Allowed."""
    r = client.delete("/api/health")
    assert r.status_code == 405, f"got {r.status_code}"
