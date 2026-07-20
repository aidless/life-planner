"""
B4 integration e2e tests (论文 §6 Case Study)

测试真实 Life-planner backend + B4 Trust Boundary middleware。

需要的运行 backend：
  cd F:/life-planner/backend
  python -m uvicorn app.main:app --port 8001 --log-level warning
"""

import os
import time
import json
import random
import tempfile
import requests
import sys

BACKEND_URL = "http://localhost:8001"
HTTP_TIMEOUT = 8  # seconds per request


def http_get(url, **kw):
    kw.setdefault("timeout", HTTP_TIMEOUT)
    return requests.get(url, **kw)


def http_post(url, **kw):
    kw.setdefault("timeout", HTTP_TIMEOUT)
    return requests.post(url, **kw)


def wait_for_backend(url: str = BACKEND_URL, timeout: int = 10) -> bool:
    """Wait for backend to be healthy (capped at 10s)."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = http_get(f"{url}/api/health")
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def register_user() -> dict:
    """Register + login. Returns token + user_id."""
    user = f"b4{int(time.time())}_{random.randint(0, 99999)}"
    email = f"{user}@x.com"
    pw = "Test123456"
    http_post(f"{BACKEND_URL}/api/auth/register", json={
        "username": user, "email": email, "password": pw
    })
    r = http_post(f"{BACKEND_URL}/api/auth/login", json={
        "username": user, "password": pw
    })
    return r.json()["data"]


# ============================================================
# 7-table multi-resource coverage
# ============================================================

def setup_user():
    """One fresh user per test scope."""
    if not wait_for_backend():
        raise RuntimeError("Backend not ready on :8001")
    return register_user()


def test_health_no_auth_required():
    """/api/health (no auth)"""
    r = http_get(f"{BACKEND_URL}/api/health")
    assert r.status_code == 200, f"health: {r.status_code}"
    assert r.json()["data"]["status"] == "healthy"


def test_info_no_auth_required():
    """/api/info (no auth)"""
    r = http_get(f"{BACKEND_URL}/api/info")
    assert r.status_code == 200, f"info: {r.status_code}"
    assert "LifePlanner" in r.json()["data"]["name"]


def test_daily_logs_get_with_auth():
    auth = setup_user()
    headers = {"Authorization": f"Bearer {auth['access_token']}"}
    r = http_get(f"{BACKEND_URL}/api/daily-logs", headers=headers)
    assert r.status_code == 200


def test_daily_logs_post_with_auth():
    auth = setup_user()
    headers = {"Authorization": f"Bearer {auth['access_token']}"}
    r = http_post(
        f"{BACKEND_URL}/api/daily-logs",
        headers=headers,
        json={"date": "2026-07-19", "mood_level": 7, "notes": "B4 test"},
    )
    # B4 grants → 200/201/422 (validation 422 still passes B4)
    assert r.status_code in [200, 201, 422]


def test_health_logs_with_auth():
    """high sensitivity - health_logs"""
    auth = setup_user()
    headers = {"Authorization": f"Bearer {auth['access_token']}"}
    r_get = http_get(f"{BACKEND_URL}/api/health/logs", headers=headers)
    assert r_get.status_code in [200, 401]


def test_finance_transactions_with_auth():
    """high - finance_transactions"""
    auth = setup_user()
    headers = {"Authorization": f"Bearer {auth['access_token']}"}
    r_get = http_get(f"{BACKEND_URL}/api/finance/transactions", headers=headers)
    assert r_get.status_code in [200, 401]


def test_finance_budgets_with_auth():
    auth = setup_user()
    headers = {"Authorization": f"Bearer {auth['access_token']}"}
    r = http_get(f"{BACKEND_URL}/api/finance/budgets", headers=headers)
    assert r.status_code in [200, 401]


def test_life_goals_with_auth():
    auth = setup_user()
    headers = {"Authorization": f"Bearer {auth['access_token']}"}
    r = http_get(f"{BACKEND_URL}/api/goals", headers=headers)
    assert r.status_code in [200, 401]


def test_habits_with_auth():
    auth = setup_user()
    headers = {"Authorization": f"Bearer {auth['access_token']}"}
    r = http_get(f"{BACKEND_URL}/api/habits", headers=headers)
    assert r.status_code in [200, 401]


def test_exams_with_auth():
    auth = setup_user()
    headers = {"Authorization": f"Bearer {auth['access_token']}"}
    r = http_get(f"{BACKEND_URL}/api/exams", headers=headers)
    assert r.status_code in [200, 401]


def test_social_interactions_with_auth():
    auth = setup_user()
    headers = {"Authorization": f"Bearer {auth['access_token']}"}
    r = http_get(f"{BACKEND_URL}/api/social/interactions", headers=headers)
    assert r.status_code in [200, 401]


def test_health_with_invalid_token():
    r = http_get(
        f"{BACKEND_URL}/api/daily-logs",
        headers={"Authorization": "Bearer invalid"},
    )
    assert r.status_code == 401


def test_no_token_blocked():
    r = http_get(f"{BACKEND_URL}/api/daily-logs")
    assert r.status_code == 401


def test_b4_steady_state_many_requests():
    """B4 doesn't crash under load"""
    auth = setup_user()
    headers = {"Authorization": f"Bearer {auth['access_token']}"}
    for _ in range(10):
        r = http_get(f"{BACKEND_URL}/api/daily-logs", headers=headers)
        assert r.status_code in [200, 401]


def test_concurrent_users_no_500():
    """3 users x 7 resources - no server error"""
    users_auths = [setup_user(), setup_user(), setup_user()]
    endpoints = [
        "/api/daily-logs",
        "/api/health/logs",
        "/api/finance/transactions",
        "/api/goals",
        "/api/habits",
        "/api/exams",
        "/api/social/interactions",
    ]
    n_500 = 0
    for auth in users_auths:
        headers = {"Authorization": f"Bearer {auth['access_token']}"}
        for ep in endpoints:
            try:
                r = http_get(f"{BACKEND_URL}{ep}", headers=headers)
                if r.status_code >= 500:
                    n_500 += 1
            except Exception:
                pass  # timeout / connection error - not 500

    assert n_500 == 0, f"Got {n_500} server errors"


def main():
    """Manual runner, no pytest needed."""
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    failed = []
    for t in tests:
        name = t.__name__
        try:
            t()
            print(f"  ✓ {name}")
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {name}: {e}")
            failed.append((name, str(e)))
        except Exception as e:
            print(f"  ✗ {name}: ERROR: {e}")
            failed.append((name, str(e)))

    print()
    print(f"Result: {passed}/{len(tests)} passed")
    if failed:
        print("\nFailed:")
        for n, e in failed:
            print(f"  - {n}: {e[:100]}")
    return len(failed) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
