"""recommend_push — 定时计算全用户推荐并写入通知箱.

cron:
    0 8  * * * cd /data3/projects/life-planner/backend && venv/bin/python scripts/recommend_push.py --slot morning
    0 21 * * * cd /data3/projects/life-planner/backend && venv/bin/python scripts/recommend_push.py --slot evening

Manual:
    venv/bin/python scripts/recommend_push.py --slot manual [--user-id 123]

Idempotent: same (user, date, slot, rule) notifications are de-duplicated
in services.save_run, so overlapping runs are safe.
"""

import argparse
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

import app.main  # noqa: F401 — register all models for create_all
from app.database import SessionLocal, engine
from app.shared.base_model import Base
from app.modules.auth.models import User  # noqa: F401
from app.modules.recommend import services as rec_svc
from sqlalchemy import select


def push_for_user(db, user_id: int, slot: str) -> dict:
    items = rec_svc.compute_today(db, user_id)
    rec_svc.save_run(db, user_id, items, slot)
    highs = [i for i in items if i.get("priority") == "high"]
    return {"user_id": user_id, "total": len(items), "high": len(highs)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", default="manual",
                    choices=["manual", "morning", "evening"])
    ap.add_argument("--user-id", type=int, default=None)
    args = ap.parse_args()

    Base.metadata.create_all(bind=engine)  # ensure recommend tables exist
    db = SessionLocal()
    try:
        if args.user_id:
            ids = [args.user_id]
        else:
            ids = list(db.execute(select(User.id)).scalars().all())
        results = [push_for_user(db, uid, args.slot) for uid in ids]
    finally:
        db.close()

    total = sum(r["total"] for r in results)
    highs = sum(r["high"] for r in results)
    print(f"slot={args.slot} users={len(results)} "
          f"recommendations={total} high={highs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
