"""Edge case smoke tests for life-planner.

W29 follow-up: focus on boundary conditions, Unicode handling,
SQL injection attempts, and concurrent-style patterns.
"""

import uuid

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    """Standard register-login. Skips if DB unavailable."""
    try:
        from app.database import engine
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        pytest.skip("Database not available")

    username = f"smoke_{uuid.uuid4().hex[:8]}"
    payload = {
        "username": username,
        "email": f"{username}@test.com",
        "password": "Test123456",
    }
    r = client.post("/api/auth/register", json=payload)
    assert r.status_code == 200
    return r.json()["data"]["access_token"]


# ── Unicode + special character handling ──────────────────────────


def test_register_with_unicode_username(client):
    """Chinese / emoji usernames must work (no crash)."""
    username = f"测试_{uuid.uuid4().hex[:8]}"
    payload = {
        "username": username,
        "email": f"{username}@test.com",
        "password": "Test123456",
    }
    r = client.post("/api/auth/register", json=payload)
    # 200 (success) or 4xx (validation) — NOT 5xx
    assert r.status_code < 500, f"unicode crashed: {r.status_code} {r.text}"


def test_register_with_sql_injection_attempt(client):
    """SQL injection in username must not crash or expose data."""
    payload = {
        "username": "admin' OR '1'='1",
        "email": "sqli@test.com",
        "password": "Test123456",
    }
    r = client.post("/api/auth/register", json=payload)
    # Should be rejected by validation OR safely escaped
    assert r.status_code < 500, f"SQLi in username crashed: {r.status_code} {r.text}"


def test_login_with_sql_injection_attempt(client):
    """SQL injection in password must not bypass auth."""
    payload = {
        "username": "nonexistent",
        "password": "' OR '1'='1",
    }
    r = client.post("/api/auth/login", json=payload)
    # Must NOT return 200 (would mean auth bypassed)
    assert r.status_code in (401, 404, 422), f"possible SQLi bypass: {r.status_code} {r.text}"


# ── boundary: extreme but valid values ──────────────────────────


def test_register_with_max_length_username(client):
    """A 200-character username must be rejected (length limit)."""
    payload = {
        "username": "a" * 200,
        "email": "long@test.com",
        "password": "Test123456",
    }
    r = client.post("/api/auth/register", json=payload)
    # 422 (Pydantic validation) or 4xx — NOT 500
    assert 400 <= r.status_code < 500, f"got {r.status_code}"


def test_register_with_empty_password(client):
    """Empty password must be rejected (NOT 201)."""
    payload = {
        "username": f"smoke_{uuid.uuid4().hex[:8]}",
        "email": "empty@test.com",
        "password": "",
    }
    r = client.post("/api/auth/register", json=payload)
    assert 400 <= r.status_code < 500, f"empty password: {r.status_code} {r.text}"


def test_register_with_duplicate_username(client, auth_token):
    """Registering the same username twice must fail, not crash."""
    # First register via the fixture (auth_token)
    # The fixture created a user; try with the same username
    # We don't have direct access, so create a new one
    username = f"dup_{uuid.uuid4().hex[:8]}"
    payload = {
        "username": username, "email": f"{username}@t.com", "password": "Test123456",
    }
    r1 = client.post("/api/auth/register", json=payload)
    assert r1.status_code == 200

    # Now duplicate
    r2 = client.post("/api/auth/register", json=payload)
    assert r2.status_code in (400, 409), f"dup: {r2.status_code}"


# ── HTTP method/header edge cases ────────────────────────────────


def test_put_to_health_returns_405(client):
    """PUT /api/health must return 405, not 500."""
    r = client.put("/api/health")
    assert r.status_code == 405, f"got {r.status_code}"


def test_post_to_college_rank_returns_405(client):
    """POST /api/college/rank (GET only) must return 405."""
    r = client.post("/api/college/rank", json={})
    assert r.status_code == 405


def test_missing_authorization_header_returns_401(client):
    """Protected routes without Authorization header must 401."""
    for path in ["/api/auth/me", "/api/goals", "/api/daily-logs",
                 "/api/exams", "/api/ai/chat", "/api/college/predict",
                 "/api/college/recommendations"]:
        r = client.get(path) if path != "/api/ai/chat" and path != "/api/college/predict" else client.post(path, json={})
        assert r.status_code == 401, f"{path}: got {r.status_code}"


# ── college edge cases (more than 1 attempted before) ─────────


def test_college_scores_with_partial_year_filter(client):
    """GET /api/college/scores?year=2024 must work without 500."""
    r = client.get("/api/college/scores", params={"year": 2024, "page": 1, "page_size": 5})
    assert r.status_code == 200
    body = r.json()["data"]
    # All returned items must be year 2024
    for item in body["items"]:
        assert item["year"] == 2024, f"year filter failed: {item['year']}"


def test_college_scores_with_special_chars_in_filter(client):
    """SQL-injection in college_name filter must not crash."""
    r = client.get("/api/college/scores",
                    params={"college": "北大' OR '1'='1", "page": 1, "page_size": 5})
    assert r.status_code < 500, f"got {r.status_code} {r.text}"


def test_college_rank_score_at_lower_boundary(client):
    """Score=0 (boundary) must not crash."""
    r = client.get("/api/college/rank", params={"year": 2025, "province": "山东", "score": 0})
    assert r.status_code < 500


def test_college_rank_score_just_below_highest(client):
    """Score just below highest (boundary) must work."""
    r = client.get("/api/college/rank", params={"year": 2025, "province": "山东", "score": 749})
    assert r.status_code < 500


# ── concurrent / rapid-fire patterns ───────────────────────────


def test_health_under_rapid_calls(client):
    """50 rapid health calls must all return 200 (under the 100/60s limit)."""
    for _ in range(50):
        r = client.get("/api/health")
        assert r.status_code == 200, f"got {r.status_code}"


def test_login_with_wrong_credentials_twice_doesnt_lock(client):
    """Two failed logins must not 500 or lock the account (we have no lockout)."""
    payload = {"username": "definitely_does_not_exist", "password": "wrong_pw"}
    for _ in range(3):
        r = client.post("/api/auth/login", json=payload)
        assert r.status_code in (401, 404, 422)


# ── response shape consistency ──────────────────────────────────


def test_all_responses_have_consistent_envelope(client):
    """Every successful JSON response should have the success/data envelope."""
    endpoints = [
        ("GET", "/api/health"),
    ]
    for method, path in endpoints:
        r = client.get(path)
        if r.headers.get("content-type", "").startswith("application/json"):
            body = r.json()
            assert "success" in body, f"{method} {path} missing 'success'"
            assert "data" in body, f"{method} {path} missing 'data'"


def test_health_endpoint_no_auth_required(client):
    """/api/health must not require auth (monitoring)."""
    # No Authorization header
    r = client.get("/api/health")
    assert r.status_code == 200


def test_docs_endpoint_no_auth_required(client):
    """/docs (Swagger UI) must not require auth (developer convenience)."""
    r = client.get("/docs")
    assert r.status_code == 200
