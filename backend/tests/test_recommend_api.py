"""P5 API tests — today/history/notifications + graceful no-LLM downgrade.

P6: conftest 把 DATABASE_URL 指到独立测试库, 本文件用户只进测试库,
不再需要 E2E 门清零（P3-3 users-zero 规则只约束正式库）。
"""

import uuid

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


@pytest.fixture
def auth_headers(client):
    username = f"rec_{uuid.uuid4().hex[:8]}"
    r = client.post("/api/auth/register", json={
        "username": username,
        "email": f"{username}@test.com",
        "password": "Test123456",
    })
    assert r.status_code == 200, f"register failed: {r.text}"
    token = r.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_today_requires_auth(client):
    r = client.get("/api/recommend/today")
    assert r.status_code == 401


def test_today_seeded_user_returns_structured_items(client, auth_headers):
    # 注册自动注入 30 天示例数据（W35），新用户非空：断言推荐结构而非 EMPTY
    # （EMPTY 空用户路径由纯规则单测 test_empty_user_gets_onboarding_only 覆盖）
    r = client.get("/api/recommend/today", headers=auth_headers)
    assert r.status_code == 200, f"today failed: {r.text}"
    body = r.json()
    assert body["success"] is True
    data = body["data"]
    assert len(data["items"]) > 0
    for i in data["items"]:
        assert set(i) >= {"rule", "module", "priority", "title",
                          "reason", "action_link", "computed_at"}
        assert i["priority"] in ("high", "medium", "low")
    # no ANTHROPIC_API_KEY in CI -> must downgrade, never 500/None-crash
    assert data["coach_mode"] == "rule"
    assert data["coach_note"] is None


def test_history_and_notifications_empty(client, auth_headers):
    r = client.get("/api/recommend/history", headers=auth_headers)
    assert r.status_code == 200 and r.json()["data"] == []
    r = client.get("/api/recommend/notifications", headers=auth_headers)
    assert r.status_code == 200 and r.json()["data"] == []


def test_read_missing_notification_ok(client, auth_headers):
    r = client.post("/api/recommend/notifications/999999/read",
                    headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["data"] == {"updated": False}


def test_push_idempotent_same_rule_same_day(client, auth_headers):
    """save_run twice with same high item -> one run each, one notification."""
    from app.database import SessionLocal
    from app.modules.recommend import services as rec_svc
    from sqlalchemy import select
    from app.modules.auth.models import User

    token_user = client.get("/api/auth/me", headers=auth_headers).json()["data"]
    db = SessionLocal()
    try:
        uid = db.execute(
            select(User.id).where(User.username == token_user["username"])
        ).scalars().one()
        item = {"rule": "H1", "module": "habits", "priority": "high",
                "title": "t", "reason": "r", "action_link": "/habits",
                "computed_at": "2026-09-07"}
        rec_svc.save_run(db, int(uid), [item], "morning", today="2026-09-07")
        rec_svc.save_run(db, int(uid), [item], "morning", today="2026-09-07")
        notifs = rec_svc.list_notifications(db, int(uid))
        h1_today = [n for n in notifs
                    if n.rule == "H1" and n.date == "2026-09-07"]
        assert len(h1_today) == 1
        hist = rec_svc.list_history(db, int(uid))
        assert any(h["date"] == "2026-09-07" and h["slot"] == "morning"
                   for h in hist)
        # mark read round-trips
        assert rec_svc.mark_read(db, int(uid), h1_today[0].id) is True
        assert rec_svc.list_notifications(
            db, int(uid), unread_only=True) == [
            n for n in rec_svc.list_notifications(db, int(uid)) if n.is_read == 0]
    finally:
        db.close()
