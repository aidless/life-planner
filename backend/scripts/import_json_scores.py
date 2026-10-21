#!/usr/bin/env python3
"""数据入库（立意收缩·支柱2）：raw JSON → college_scores / province_ranks 表。

可复算：全部读 backend/data/raw 下已清洗 JSON，字段映射写死在脚本里；
幂等：目标表已有行时默认跳过，--force 走「清空重导」。行程学院/位次是
参考数据（非用户数据），users 表零写入。

用法（backend/ cwd）：
    ./venv/bin/python scripts/import_json_scores.py           # 幂等导入 + 校验
    ./venv/bin/python scripts/import_json_scores.py --force   # 清空重导
    ./venv/bin/python scripts/import_json_scores.py --db /path/db
"""
import argparse
import json
import sqlite3
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent
RAW_SCORES = sorted((BACKEND / "data" / "raw" / "scores").glob("*.json"))
RAW_RANKS = sorted((BACKEND / "data" / "raw" / "ranks").glob("*.json"))

DEFAULT_DB = BACKEND / "life_planner.db"

SCORE_COLS = [
    "year", "province", "college_name", "major_name", "batch",
    "min_score", "avg_score", "max_score", "min_rank", "source",
    "subject_type", "is_deleted",
]
RANK_COLS = ["year", "province", "score", "rank", "batch_category", "is_deleted"]


def _f(v):
    return None if v is None else v


def normalize_score(r: dict) -> dict | None:
    """一条 score JSON → 一行 college_scores；返回列值 dict。"""
    year = r.get("year")
    province = r.get("province")
    college_name = r.get("college_name")
    if not (year and province and college_name):
        return None
    major_name = r.get("major_name")
    if not major_name and r.get("major_group_code"):
        major_name = f"专业组{r['major_group_code']}"
    if not major_name:
        major_name = ""  # 列 NOT NULL，保底空串
    return {
        "year": int(year),
        "province": province,
        "college_name": college_name,
        "major_name": major_name,
        "batch": _f(r.get("batch")),
        "min_score": _f(r.get("min_score")),
        "avg_score": _f(r.get("avg_score")),
        "max_score": _f(r.get("max_score")),
        "min_rank": _f(r.get("min_rank")),
        "source": _f(r.get("source")),
        "subject_type": _f(r.get("subject_type") or r.get("category")),
        "is_deleted": 0,
    }


def normalize_rank(r: dict) -> dict | None:
    if not (r.get("year") and r.get("province")):
        return None
    return {
        "year": int(r["year"]),
        "province": r["province"],
        "score": int(r["score"]),
        "rank": int(r["rank"]),
        "batch_category": _f(r.get("batch_category")),
        "is_deleted": 0,
    }


def load_rows():
    scores = []
    for f in RAW_SCORES:
        n = 0
        for r in json.loads(f.read_text(encoding="utf-8")):
            row = normalize_score(r)
            if row is None:
                continue
            scores.append(row)
            n += 1
        print(f"  scores  {f.name}: {n} 行")
    ranks = []
    for f in RAW_RANKS:
        n = 0
        for r in json.loads(f.read_text(encoding="utf-8")):
            row = normalize_rank(r)
            if row is None:
                continue
            ranks.append(row)
            n += 1
        print(f"  ranks   {f.name}: {n} 行")
    return scores, ranks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--force", action="store_true", help="清空 college_scores/province_ranks 后重导")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    conn.execute("PRAGMA foreign_keys=OFF")
    cur = conn.cursor()

    pre_scores = cur.execute("SELECT COUNT(*) FROM college_scores").fetchone()[0]
    pre_ranks = cur.execute("SELECT COUNT(*) FROM province_ranks").fetchone()[0]
    pre_users = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    print(f"导入前: college_scores={pre_scores} province_ranks={pre_ranks} users={pre_users}")

    if not args.force and (pre_scores or pre_ranks):
        print("目标表已有数据，跳过（幂等）。如需重导请加 --force。")
        conn.close()
        return 0

    scores, ranks = load_rows()

    # 去重（同表内可能重复）：(year, province, college_name, major_name) 保留第一条
    seen = set()
    unique_scores = []
    for s in scores:
        key = (s["year"], s["province"], s["college_name"], s["major_name"])
        if key in seen:
            continue
        seen.add(key)
        unique_scores.append(s)

    seen_r = set()
    unique_ranks = []
    for r in ranks:
        key = (r["year"], r["province"], r["score"])
        if key in seen_r:
            continue
        seen_r.add(key)
        unique_ranks.append(r)

    if args.force:
        cur.execute("DELETE FROM college_scores")
        cur.execute("DELETE FROM province_ranks")

    q_scores = f"INSERT OR IGNORE INTO college_scores ({','.join(SCORE_COLS)}) VALUES ({','.join('?' * len(SCORE_COLS))})"
    q_ranks = f"INSERT OR IGNORE INTO province_ranks ({','.join(RANK_COLS)}) VALUES ({','.join('?' * len(RANK_COLS))})"

    cur.executemany(q_scores, [tuple(s[c] for c in SCORE_COLS) for s in unique_scores])
    cur.executemany(q_ranks, [tuple(r[c] for c in RANK_COLS) for r in unique_ranks])
    conn.commit()

    post_scores = cur.execute("SELECT COUNT(*) FROM college_scores").fetchone()[0]
    post_ranks = cur.execute("SELECT COUNT(*) FROM province_ranks").fetchone()[0]
    post_users = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    print(f"\n汇总: 原始 scores={len(scores)} → 去重={len(unique_scores)} → 入库={post_scores}")
    print(f"      原始 ranks={len(ranks)} → 去重={len(unique_ranks)} → 入库={post_ranks}")
    print(f"      users={post_users}（应保持 0，未写入用户数据）")

    # 复算校验：按省/年分组行数
    rows = cur.execute(
        "SELECT province, year, COUNT(*) FROM college_scores GROUP BY province, year ORDER BY province, year"
    ).fetchall()
    print("\n按省/年分组（可复算）:")
    for p, y, n in rows:
        print(f"  {p} {y}: {n} 行")
    rows = cur.execute(
        "SELECT province, year, COUNT(*) FROM province_ranks GROUP BY province, year"
    ).fetchall()
    for p, y, n in rows:
        print(f"  rank {p} {y}: {n} 行")

    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())