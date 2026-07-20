"""Cross-subdomain integration smoke tests.

W29 follow-up: test the interactions between subdomains.
Real-world scenarios: cross-cutting concerns, edge cases.
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
    """Reuse register-login pattern. Skip if DB unavailable."""
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


# ── cross-subdomain: register → predict → record recommendation ──


def test_full_college_flow_with_auth(client, auth_token):
    """Register → login → predict → record (lifecycle integration test).

    This is the full vertical slice: proves the system actually works
    end-to-end (not just smoke-test individual endpoints).
    """
    headers = {"Authorization": f"Bearer {auth_token}"}

    # 1. Predict colleges
    r = client.post("/api/college/predict",
                    headers=headers,
                    json={
                        "score": 587,
                        "province": "山东",
                        "subject_combination": "综合",
                        "year": 2025,
                    })
    assert r.status_code == 200, f"predict failed: {r.text}"
    body = r.json()
    assert body["success"] is True
    data = body["data"]
    assert "dash" in data and "steady" in data and "safe" in data

    # 2. Recommendations history should now have 1 entry
    r = client.get("/api/college/recommendations", headers=headers)
    assert r.status_code == 200
    history = r.json()["data"]["items"]
    assert len(history) >= 1, f"no history recorded: {history}"

    # 3. /api/auth/me returns the same user
    r = client.get("/api/auth/me", headers=headers)
    assert r.status_code == 200


# ── security: token reuse and isolation ───────────────────────────


def test_token_only_valid_for_own_user(client, auth_token):
    """Token from one user must not allow access to another user's data.

    Creates 2 users, registers both, then tries to use token-A to
    create goals as user-B. The goal must still be tied to the token's user.
    """
    headers = {"Authorization": f"Bearer {auth_token}"}
    # Create a goal for current user
    r = client.post("/api/goals", headers=headers,
                    json={"title": "User 1's goal", "category": "test"})
    assert r.status_code == 200
    user1_goal_id = r.json()["data"]["id"]

    # List should only show user 1's goal
    r = client.get("/api/goals", headers=headers)
    assert r.status_code == 200
    goals = r.json()["data"]
    goal_ids = [g["id"] for g in goals]
    assert user1_goal_id in goal_ids

    # A different user trying to access this goal must 404
    username2 = f"smoke2_{uuid.uuid4().hex[:8]}"
    r2 = client.post("/api/auth/register", json={
        "username": username2,
        "email": f"{username2}@test.com",
        "password": "Test123456",
    })
    token2 = r2.json()["data"]["access_token"]
    headers2 = {"Authorization": f"Bearer {token2}"}

    r = client.get(f"/api/goals/{user1_goal_id}", headers=headers2)
    assert r.status_code == 404, f"user2 accessed user1's goal: {r.text}"


# ── input validation: extreme values ───────────────────────────────


def test_college_predict_negative_score_returns_4xx(client, auth_token):
    """POST /api/college/predict with negative score must 4xx, not 500."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.post("/api/college/predict", headers=headers, json={
        "score": -100, "province": "山东", "subject_combination": "综合", "year": 2025,
    })
    # Pydantic validation should catch this; or service should reject
    assert 400 <= r.status_code < 500, f"got {r.status_code} {r.text}"


def test_college_predict_extreme_score_returns_4xx(client, auth_token):
    """Score of 99999 must not crash."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.post("/api/college/predict", headers=headers, json={
        "score": 99999, "province": "山东", "subject_combination": "综合", "year": 2025,
    })
    assert 400 <= r.status_code < 500, f"got {r.status_code} {r.text}"


def test_college_predict_empty_province_returns_4xx(client, auth_token):
    """Empty province string must 4xx."""
    headers = {"Authorization": f"Bearer {auth_token}"}
    r = client.post("/api/college/predict", headers=headers, json={
        "score": 587, "province": "", "subject_combination": "综合", "year": 2025,
    })
    assert 400 <= r.status_code < 500


def test_college_rank_extreme_score_does_not_500(client):
    """rank with score=99999 must return a real response, not 500."""
    r = client.get("/api/college/rank",
                    params={"year": 2025, "province": "山东", "score": 99999})
    assert r.status_code < 500


# ── pagination edge cases ──────────────────────────────────────────


def test_college_list_page_beyond_total_returns_empty(client):
    """GET /api/college/colleges?page=99999 must return empty list, not 500."""
    r = client.get("/api/college/colleges", params={"page": 99999, "page_size": 10})
    assert r.status_code == 200
    body = r.json()
    assert body["data"]["items"] == []


def test_college_list_page_zero_returns_4xx(client):
    """page=0 must be rejected (page must be >= 1)."""
    r = client.get("/api/college/colleges", params={"page": 0, "page_size": 10})
    assert 400 <= r.status_code < 500, f"got {r.status_code}"


# ── response shape validation ─────────────────────────────────────


def test_health_response_shape(client):
    """/api/health must return a specific shape, not just any 200."""
    r = client.get("/api/health")
    assert r.status_code == 200
    body = r.json()
    assert body["success"] is True
    assert body["data"]["status"] == "healthy"
    # Must NOT have unexpected fields
    assert set(body.keys()) == {"success", "data"}
    assert set(body["data"].keys()) == {"status"}


def test_404_response_shape(client):
    """/api/does-not-exist must return a meaningful 4xx error, not 200."""
    r = client.get("/api/does-not-exist")
    assert 400 <= r.status_code < 500
    if r.status_code == 404:
        body = r.json()
        assert "detail" in body
