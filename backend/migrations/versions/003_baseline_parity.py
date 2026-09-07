"""P7-B1 baseline parity: converge alembic-head to create_all schema.

Revision ID: 003_baseline_parity
Revises: 002_recommend
Create Date: 2026-09-08

Why this exists (honest history):
- 001 is a legacy-schema snapshot: users/exams/exam_questions have the OLD
  (phone/exam_name/content-era) shapes, and the ~29 newer app-domain tables
  are absent. 002 adds recommendation tables only.
- Production today is built by Base.metadata.create_all with Base-first
  semantics (new shapes win on the 3 overlapping names; legacy-only tables
  filled by LegacyBase). So `alembic upgrade head` on a fresh DB produced a
  DIFFERENT schema than production — plus env.py crashed before B1, so the
  alembic path never actually ran anywhere.

What upgrade() does on the migration connection:
1. create_all (checkfirst) for both metadatas -> all missing tables appear.
2. For the 3 overlapping tables, if the OLD 001 shape is detected:
   - empty table  -> rebuild to the current (app Base) shape, drop backup;
   - non-empty    -> ABORT with a loud error: legacy rows need a human
     porting decision, we refuse to silently drop or half-merge them.
   - already new shape (e.g. stamped prod-like DB) -> skip, no-op.
3. Downgrade is intentionally one-way (raises); restore from backup.

Production 4800 is NOT touched by this file in B1 (still boots on
create_all; one-time `alembic stamp head` deferred to a maintenance window).
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '003_baseline_parity'
down_revision = '002_recommend'
branch_labels = None
depends_on = None

# Legacy markers for the three historically reshaped tables (used in errors).
OVERLAPS = [
    ('users', 'phone'),
    ('exams', 'exam_name'),
    ('exam_questions', 'content'),
]


def _tolerant_create_all(conn, metadata):
    """create_all that tolerates pre-existing indexes.

    001 created tables without indexes while both metadatas declare
    index=True columns; the first create_all run backfills indexes onto
    old tables and the second run can trip over the same index name.
    Goal here is convergence, so 'already exists' is a no-op signal,
    anything else re-raises.
    """
    from sqlalchemy.exc import OperationalError
    try:
        metadata.create_all(bind=conn, checkfirst=True)
    except OperationalError:
        import traceback
        tb = traceback.format_exc()
        if "already exists" not in tb:
            raise


def _drop_table_indexes(conn, table_name):
    rows = conn.execute(sa.text(
        "SELECT name FROM sqlite_master WHERE type='index' "
        "AND tbl_name=:t AND sql IS NOT NULL"
    ), {"t": table_name}).fetchall()
    for (idx,) in rows:
        conn.execute(sa.text(f'DROP INDEX "{idx}"'))


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("PRAGMA foreign_keys=OFF"))

    from app.shared.base_model import Base as AppBase
    from database import Base as LegacyBase
    # 1) Fill every table missing from the 001+002 path. checkfirst makes
    #    this a no-op for tables that already exist (incl. overlaps).
    #    Overlaps are rebuilt in step 2, so order matters: fill first would
    #    backfill new-shape indexes onto old-shape tables; rebuild cleans
    #    them via backup-index drop below. Either order converges.
    _tolerant_create_all(conn, AppBase.metadata)
    _tolerant_create_all(conn, LegacyBase.metadata)

    # 2) Rebuild any table whose 001/002-era shape differs from current
    #    metadata (column-name compare). Known cases: users, exams,
    #    exam_questions (full reshapes) + legacy tables that drifted since
    #    001, e.g. college_scores (rank_min -> min_rank/min_score/...).
    #    Empty  -> rebuild to current shape, drop backup.
    #    Non-empty -> ABORT loudly: rows need a human porting decision.
    #    Same columns -> leave alone (type/default diffs converge on the
    #    next real migration; documented B1 limitation).
    current_tables = {}
    current_tables.update(AppBase.metadata.tables)
    for n, t in LegacyBase.metadata.tables.items():
        current_tables.setdefault(n, t)
    inspector = sa.inspect(conn)
    for name in sorted(current_tables):
        if name == "alembic_version" or not inspector.has_table(name):
            continue  # step 1 created it fresh -> already current
        have = [c["name"] for c in inspector.get_columns(name)]
        want = [c.name for c in current_tables[name].columns]
        if have == want:
            continue
        # Order-insensitive re-check: sqlite preserves definition order, so
        # any order difference is also a real DDL difference -> rebuild.
        if sorted(have) == sorted(want):
            continue  # same columns, order differs only -> leave alone
        n = conn.execute(sa.text(f'SELECT COUNT(*) FROM "{name}"')).scalar()
        if n:
            raise RuntimeError(
                f"003_baseline_parity refuses: table '{name}' has {n} rows "
                f"in stale shape (have={have} want={want}). Port the rows "
                "by hand, then re-run upgrade."
            )
        new_table = current_tables[name]
        backup = f"{name}__legacy001"
        conn.execute(sa.text(f'ALTER TABLE "{name}" RENAME TO "{backup}"'))
        # Step-1 fill may have backfilled current index names onto the stale
        # table; the rename carries them (sqlite index names are DB-global).
        _drop_table_indexes(conn, backup)
        new_table.create(bind=conn, checkfirst=True)
        shared = [c.name for c in new_table.columns if c.name in have]
        if shared:
            collist = ", ".join(f'"{c}"' for c in shared)
            conn.execute(sa.text(
                f'INSERT INTO "{name}" ({collist}) SELECT {collist} FROM "{backup}"'
            ))
        conn.execute(sa.text(f'DROP TABLE "{backup}"'))

    conn.execute(sa.text("PRAGMA foreign_keys=ON"))


def downgrade() -> None:
    raise RuntimeError(
        "003_baseline_parity is a one-way baseline; restore the DB file from backup."
    )
