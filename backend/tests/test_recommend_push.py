"""P7-B4: 推送结构化事件（build_event/run_push）单测.

跑在隔离测试库（conftest 把 DATABASE_URL 指到 tests/test_isolated.db），
不碰正式库。
"""

import json

from scripts import recommend_push as rp


def test_build_event_keys_and_totals():
    results = [{"user_id": 7, "total": 3, "high": 1},
               {"user_id": 9, "total": 2, "high": 0}]
    ev = rp.build_event("evening", results, [], ts="2026-09-07T21:00:01+08:00")
    assert ev["slot"] == "evening"
    assert ev["users"] == 2
    assert ev["recommendations"] == 5
    assert ev["high"] == 1
    assert ev["errors"] == []
    # JSONL：单行、可解析、中文不转义
    line = json.dumps(ev, ensure_ascii=False)
    assert "\n" not in line
    assert json.loads(line) == ev


def test_run_push_isolates_per_user_failure(monkeypatch):
    """一个用户炸了，同批其他用户照常推送，errors 点名肇事者."""
    from app.database import SessionLocal
    monkeypatch.setattr(
        rp.rec_svc, "compute_today",
        lambda db, uid: (_ for _ in ()).throw(RuntimeError("boom"))
        if uid == 999 else [{"priority": "high", "rule": "T1",
                             "title": "t", "reason": "r", "module": "m"}],
    )
    saved = []
    monkeypatch.setattr(
        rp.rec_svc, "save_run",
        lambda db, uid, items, slot: saved.append(uid),
    )
    results, errors = rp.run_push(SessionLocal(), [999, 1000], "manual")
    assert [r["user_id"] for r in results] == [1000]
    assert results[0]["total"] == 1 and results[0]["high"] == 1
    assert len(errors) == 1 and errors[0]["user_id"] == 999
    assert "RuntimeError" in errors[0]["error"]
    assert saved == [1000]


def test_build_event_counts_errors_in_users():
    ev = rp.build_event("morning", [{"user_id": 1, "total": 0, "high": 0}],
                        [{"user_id": 2, "error": "X"}],
                        ts="2026-09-07T08:00:01+08:00")
    assert ev["users"] == 2
    assert ev["recommendations"] == 0
