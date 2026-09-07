"""recommend_push — 定时计算全用户推荐并写入通知箱.

cron（P7-B4：日志落持久目录，不再放 /tmp，机器重启不再丢证据）:
    0 8  * * * cd /data3/projects/life-planner/backend && venv/bin/python scripts/recommend_push.py --slot morning >> logs/recommend_push.jsonl 2>&1
    0 21 * * * cd /data3/projects/life-planner/backend && venv/bin/python scripts/recommend_push.py --slot evening >> logs/recommend_push.jsonl 2>&1
    @reboot sleep 120 && cd /data3/projects/life-planner/backend && venv/bin/python scripts/recommend_push.py --slot morning >> logs/recommend_push.jsonl 2>&1
    # P6: @reboot 兜底 —— 机器若在 08:00 宕机（如 2026-09-07 晨重启致当日
    # morning 未触发），启动后补跑一次；save_run 按 (user,date,slot,rule)
    # 去重，与 08:00 自然触发重复执行也安全。

Manual:
    venv/bin/python scripts/recommend_push.py --slot manual [--user-id 123]

Output（P7-B4 结构化）: stdout 只打一行 JSON（JSONL，可直接 >> 追加进日志）::
    {"ts": "2026-09-07T21:00:01+08:00", "slot": "evening",
     "users": 2, "recommendations": 5, "high": 1,
     "results": [{"user_id": 7, "total": 3, "high": 1}],
     "errors": []}

Idempotent: same (user, date, slot, rule) notifications are de-duplicated
in services.save_run, so overlapping runs are safe.

Exit code: 0 全成功；1 至少一个用户失败（JSON 仍输出，errors 里点名）。
"""

import argparse
import json
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

import app.main  # noqa: F401 — register all models for create_all
from app.database import SessionLocal, engine
from app.shared.base_model import Base
from app.modules.auth.models import User  # noqa: F401
from app.modules.recommend import services as rec_svc
from sqlalchemy import select
from sqlalchemy.orm import Session

# 北京时间（推送时刻人类可读，机器解析走 ISO-8601 带时区）
TZ = timezone(timedelta(hours=8))


def push_for_user(db: Session, user_id: int, slot: str) -> dict:
    items = rec_svc.compute_today(db, user_id)
    rec_svc.save_run(db, user_id, items, slot)
    highs = [i for i in items if i.get("priority") == "high"]
    return {"user_id": user_id, "total": len(items), "high": len(highs)}


def run_push(db: Session, user_ids: list, slot: str) -> tuple:
    """逐用户推送，单个用户异常只记 errors，不掀翻整批（P7-B4）。"""
    results, errors = [], []
    for uid in user_ids:
        try:
            results.append(push_for_user(db, uid, slot))
        except Exception as exc:  # noqa: BLE001 — 隔离语义要求全捕获并点名
            db.rollback()
            errors.append({"user_id": uid, "error": f"{type(exc).__name__}: {exc}"})
    return results, errors


def build_event(slot: str, results: list, errors: list,
                ts: str | None = None) -> dict:
    """组装结构化推送事件（纯函数，可单测；必含 users/recommendations/high）。"""
    return {
        "ts": ts or datetime.now(TZ).isoformat(timespec="seconds"),
        "slot": slot,
        "users": len(results) + len(errors),
        "recommendations": sum(r["total"] for r in results),
        "high": sum(r["high"] for r in results),
        "results": results,
        "errors": errors,
    }


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", default="manual",
                    choices=["manual", "morning", "evening"])
    ap.add_argument("--user-id", type=int, default=None)
    args = ap.parse_args(argv)

    Base.metadata.create_all(bind=engine)  # ensure recommend tables exist
    db = SessionLocal()
    try:
        if args.user_id:
            ids = [args.user_id]
        else:
            ids = list(db.execute(select(User.id)).scalars().all())
        results, errors = run_push(db, ids, args.slot)
    finally:
        db.close()

    print(json.dumps(build_event(args.slot, results, errors),
                     ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
