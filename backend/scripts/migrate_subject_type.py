"""
Migrate database: add subject_type column to college_scores table.
Update existing Guangdong data with subject_type from JSON files.
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = "F:/life-planner/backend/life_planner.db"
PHYSICS_JSON = "F:/life-planner/backend/data/raw/scores/guangdong_2025_physics.json"
HISTORY_JSON = "F:/life-planner/backend/data/raw/scores/guangdong_2025_history.json"


def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if subject_type column exists
    cursor.execute("PRAGMA table_info(college_scores)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if "subject_type" not in columns:
        print("Adding subject_type column...")
        cursor.execute("ALTER TABLE college_scores ADD COLUMN subject_type VARCHAR(20)")
        conn.commit()
        print("Column added.")
    else:
        print("subject_type column already exists.")
    
    # Update Shandong data to 综合
    cursor.execute("UPDATE college_scores SET subject_type = '综合' WHERE province = '山东' AND subject_type IS NULL")
    shandong_updated = cursor.rowcount
    print(f"Updated {shandong_updated} Shandong records to 综合")
    
    # Load Guangdong physics data and update
    with open(PHYSICS_JSON, 'r', encoding='utf-8') as f:
        physics_data = json.load(f)
    
    physics_updated = 0
    for rec in physics_data:
        college_name = rec.get("college_name")
        major_code = rec.get("major_group_code")
        min_score = rec.get("min_score")
        min_rank = rec.get("min_rank")
        
        if college_name and major_code and min_rank is not None:
            cursor.execute(
                "UPDATE college_scores SET subject_type = '物理' WHERE province = '广东' AND college_name = ? AND major_name = ? AND min_rank = ?",
                (college_name, major_code, min_rank)
            )
            if cursor.rowcount > 0:
                physics_updated += cursor.rowcount
    
    print(f"Updated {physics_updated} Guangdong physics records")
    
    # Load Guangdong history data and update
    with open(HISTORY_JSON, 'r', encoding='utf-8') as f:
        history_data = json.load(f)
    
    history_updated = 0
    for rec in history_data:
        college_name = rec.get("college_name")
        major_code = rec.get("major_group_code")
        min_score = rec.get("min_score")
        min_rank = rec.get("min_rank")
        
        if college_name and major_code and min_rank is not None:
            cursor.execute(
                "UPDATE college_scores SET subject_type = '历史' WHERE province = '广东' AND college_name = ? AND major_name = ? AND min_rank = ? AND subject_type IS NULL",
                (college_name, major_code, min_rank)
            )
            if cursor.rowcount > 0:
                history_updated += cursor.rowcount
    
    print(f"Updated {history_updated} Guangdong history records")
    
    # Check remaining NULL subject_type
    cursor.execute("SELECT COUNT(*) FROM college_scores WHERE subject_type IS NULL")
    remaining = cursor.fetchone()[0]
    print(f"Remaining NULL subject_type: {remaining}")
    
    conn.commit()
    conn.close()
    print("Migration complete!")


if __name__ == "__main__":
    migrate()
