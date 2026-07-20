"""Smoke tests for the college module (W26 new module).

W3/W5 reports claimed this was already working. W26 builds the
actual module for the first time. These tests prove the routes
respond and stay within expected status codes.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


def test_college_rank_endpoint_responds(client):
    """GET /api/college/rank must not 5xx, even with no DB data.

    Catches missing tables / mis-typed query params.
    """
    r = client.get("/api/college/rank", params={"year": 2025, "province": "山东", "score": 587})
    # 200 with no_data, 401 without auth (if it requires auth), or 4xx - all OK
    # but not 5xx
    assert r.status_code < 500, f"rank 5xx'd: {r.status_code} {r.text}"


def test_college_scores_endpoint_responds(client):
    """GET /api/college/scores with empty filter must not 5xx."""
    r = client.get("/api/college/scores")
    assert r.status_code < 500, f"scores 5xx'd: {r.status_code} {r.text}"


def test_college_list_endpoint_responds(client):
    """GET /api/college/colleges (paginated) must not 5xx."""
    r = client.get("/api/college/colleges", params={"page": 1, "page_size": 5})
    assert r.status_code < 500, f"colleges 5xx'd: {r.status_code} {r.text}"


def test_college_predict_requires_auth(client):
    """POST /api/college/predict must require auth (401, not 5xx)."""
    r = client.post("/api/college/predict", json={
        "score": 587, "province": "山东", "subject_combination": "综合", "year": 2025,
    })
    assert r.status_code == 401, f"predict no-auth returned {r.status_code}"


def test_college_recommendations_requires_auth(client):
    """GET /api/college/recommendations must require auth."""
    r = client.get("/api/college/recommendations")
    assert r.status_code == 401, f"recommendations no-auth returned {r.status_code}"


def test_college_detail_404_for_nonexistent(client):
    """GET /api/college/colleges/{id} with bad id must return 404, not 5xx."""
    r = client.get("/api/college/colleges/999999")
    assert r.status_code == 404, f"bad id returned {r.status_code} {r.text}"
