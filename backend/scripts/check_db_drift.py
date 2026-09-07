#!/usr/bin/env python3
"""P7-B1 drift gate: alembic-head schema must equal create_all schema.

Builds two scratch sqlite DBs (never touches production):
  A: Base + Legacy create_all (what production 4800 boots with today)
  B: `alembic upgrade head` from empty (the canonical fresh-DB path)
Compares table sets and per-table column-name sets. Exit 0 on parity,
exit 1 with a diff on drift. Run:  python scripts/check_db_drift.py
"""
import os
import subprocess
import sys
import tempfile

BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BACKEND)


def schema_of(url):
    from sqlalchemy import create_engine, inspect
    eng = create_engine(url)
    insp = inspect(eng)
    out = {}
    for t in sorted(insp.get_table_names()):
        if t == "alembic_version":
            continue
        out[t] = sorted(c["name"] for c in insp.get_columns(t))
    return out


def main():
    from sqlalchemy import create_engine
    from app.modules.loader import discover
    discover()
    import models  # noqa: F401
    from app.shared.base_model import Base as AppBase
    from database import Base as LegacyBase

    tmp = tempfile.mkdtemp(prefix="b1_drift_")
    a_path = os.path.join(tmp, "a.db")
    b_path = os.path.join(tmp, "b.db")

    ea = create_engine(f"sqlite:///{a_path}")
    AppBase.metadata.create_all(bind=ea)
    LegacyBase.metadata.create_all(bind=ea)

    env = dict(os.environ, DATABASE_URL=f"sqlite:///{b_path}")
    r = subprocess.run(
        [sys.executable, "-m", "alembic", "-c", "migrations/alembic.ini", "upgrade", "head"],
        cwd=BACKEND, env=env, capture_output=True, text=True,
    )
    if r.returncode != 0:
        print("alembic upgrade head FAILED on scratch DB:\n" + r.stderr[-3000:])
        return 1

    A = schema_of(f"sqlite:///{a_path}")
    B = schema_of(f"sqlite:///{b_path}")

    ok = True
    only_a = sorted(set(A) - set(B))
    only_b = sorted(set(B) - set(A))
    if only_a:
        ok = False
        print("TABLES ONLY IN create_all:", only_a)
    if only_b:
        ok = False
        print("TABLES ONLY IN alembic-head:", only_b)
    for t in sorted(set(A) & set(B)):
        if A[t] != B[t]:
            ok = False
            print(f"COLUMN DRIFT in {t}:")
            print(f"  create_all : {A[t]}")
            print(f"  alembic    : {B[t]}")
    # New-shape assertion on the historically drifted tables.
    for t, marker, expect in [("users", "phone", "username"),
                              ("exams", "exam_name", "name"),
                              ("exam_questions", "content", "topic")]:
        if marker in B.get(t, []):
            ok = False
            print(f"STALE SHAPE: alembic {t} still has legacy column '{marker}'")
        if expect not in B.get(t, []):
            ok = False
            print(f"STALE SHAPE: alembic {t} missing current column '{expect}'")

    print(f"A tables={len(A)} B tables={len(B)} -> {'PARITY-OK' if ok else 'DRIFT'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
