"""
Import college score data from JSON files into the database.

Usage:
    python scripts/import_scores.py [json_file_path]
    
Example:
    python scripts/import_scores.py data/raw/scores/shandong_2025.json
    python scripts/import_scores.py data/raw/scores/  # import all JSON in dir
"""

import sys
import os
import json
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s:%(message)s")
logger = logging.getLogger(__name__)

# Add parent dir to path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SyncSessionLocal, Base, engine
from models.college_score import CollegeScore
from models.college_info import CollegeInfo


def load_json_files(paths: List[str]) -> List[Dict[str, Any]]:
    """Load all records from JSON file(s)."""
    all_records = []
    for p in paths:
        with open(p, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if isinstance(data, list):
            all_records.extend(data)
        else:
            logger.warning(f"JSON file {p} is not a list, skipping")
    logger.info(f"Loaded {len(all_records)} records from {len(paths)} file(s)")
    return all_records


def import_scores(records: List[Dict[str, Any]], batch_size: int = 500):
    """
    Import score records into college_scores table.
    
    Args:
        records: List of score record dicts (from JSON)
        batch_size: Commit every N records
    """
    session = SyncSessionLocal()
    inserted = 0
    skipped = 0
    
    try:
        for i, rec in enumerate(records):
            # Map JSON fields to DB fields
            # Handle new format (Guangdong 2024+) where major_name is major_group_code
            major_name = rec.get("major_name")
            if not major_name and rec.get("major_group_code"):
                major_name = f"专业组{rec.get('major_group_code')}"
            
            # Handle subject_type from category field
            subject_type = rec.get("subject_type")
            category = rec.get("category")
            if not subject_type and category:
                # Map category (物理类/历史类) to subject_type
                if "物理" in category:
                    subject_type = "物理"
                elif "历史" in category:
                    subject_type = "历史"
                else:
                    subject_type = category
            
            db_rec = CollegeScore(
                year=rec.get("year"),
                province=rec.get("province"),
                college_name=rec.get("college_name"),
                major_name=major_name,
                batch=rec.get("batch", "本科批"),
                min_score=rec.get("min_score"),
                avg_score=rec.get("avg_score"),
                max_score=rec.get("max_score"),
                min_rank=rec.get("min_rank"),
                source=rec.get("source", "unknown"),
                subject_type=subject_type,
            )
            session.add(db_rec)
            inserted += 1
            
            if (i + 1) % batch_size == 0:
                session.commit()
                logger.info(f"Committed batch: {i + 1}/{len(records)} records")
        
        session.commit()
        logger.info(f"Import complete: {inserted} inserted, {skipped} skipped")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Import failed: {e}")
        raise
    finally:
        session.close()


def import_colleges(records: List[Dict[str, Any]]):
    """
    Import unique colleges into college_info table.
    Skips colleges that already exist (by name).
    """
    session = SyncSessionLocal()
    
    # Get existing college names
    existing = set(r[0] for r in session.query(CollegeInfo.name).all())
    
    new_colleges = []
    seen = set()
    for rec in records:
        name = rec.get("college_name")
        if name and name not in existing and name not in seen:
            seen.add(name)
            new_colleges.append(CollegeInfo(
                name=name,
                province=rec.get("province"),
                updated_at=datetime.now(timezone.utc),
            ))
    
    if new_colleges:
        session.add_all(new_colleges)
        session.commit()
        logger.info(f"Imported {len(new_colleges)} new colleges into college_info")
    else:
        logger.info("No new colleges to import")
    
    session.close()


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    path_arg = sys.argv[1]
    
    # Collect JSON file paths
    json_files = []
    if os.path.isdir(path_arg):
        for f in os.listdir(path_arg):
            if f.endswith('.json'):
                json_files.append(os.path.join(path_arg, f))
        json_files.sort()
    else:
        json_files = [path_arg]
    
    if not json_files:
        logger.error(f"No JSON files found at {path_arg}")
        sys.exit(1)
    
    logger.info(f"JSON files to import: {json_files}")
    
    # Load all records
    records = load_json_files(json_files)
    
    if not records:
        logger.warning("No records to import")
        sys.exit(0)
    
    # Import colleges first (foreign key reference)
    import_colleges(records)
    
    # Import scores
    import_scores(records)


if __name__ == "__main__":
    main()
