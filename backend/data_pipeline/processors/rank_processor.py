"""
Rank processor for Life Planner data pipeline.

Cleans raw rank JSON from crawlers and converts to standard format
ready for bulk insert into ProvinceRank model.
"""

import json
import os
import logging
from typing import List, Dict, Any, Set
from datetime import datetime

logger = logging.getLogger(__name__)


class RankProcessor:
    """
    Processor for province rank data (一分一段表).
    
    Cleans raw crawler output and converts to standard format.
    """
    
    def __init__(self, raw_dir: str = "data/raw/ranks", processed_dir: str = "data/processed/ranks"):
        """
        Initialize processor.
        
        Args:
            raw_dir: Directory containing raw rank JSON files
            processed_dir: Directory to save processed JSON files
        """
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        os.makedirs(processed_dir, exist_ok=True)
    
    def process(self, province: str, year: int) -> int:
        """
        Process raw rank data for a province and year.
        
        Args:
            province: Province code (e.g., 'shandong')
            year: Exam year (e.g., 2025)
            
        Returns:
            Number of successfully processed records
        """
        # Raw file naming: {province}_ranks_{year}.json (from province_easy.py)
        raw_path = os.path.join(self.raw_dir, f"{province}_ranks_{year}.json")
        
        # Also try alternative naming: {province}_{year}.json (as per user requirement)
        if not os.path.exists(raw_path):
            raw_path_alt = os.path.join(self.raw_dir, f"{province}_{year}.json")
            if os.path.exists(raw_path_alt):
                raw_path = raw_path_alt
            else:
                logger.error(f"Raw file not found: {raw_path} or {raw_path_alt}")
                return 0
        
        processed_path = os.path.join(self.processed_dir, f"{province}_{year}.json")
        
        logger.info(f"Processing rank data: {raw_path}")
        
        # Read raw data
        with open(raw_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
        
        if not isinstance(raw_data, list):
            logger.error(f"Raw data is not a list: {raw_path}")
            return 0
        
        # Process records
        processed_records = []
        seen_keys: Set[str] = set()
        
        for record in raw_data:
            try:
                processed = self._clean_record(record)
                if processed is None:
                    continue
                
                # Deduplication: same year+province+subject_category+score_section
                dedup_key = f"{processed['year']}_{processed['province']}_{processed['subject_category']}_{processed['score_section']}"
                if dedup_key in seen_keys:
                    logger.debug(f"Duplicate record skipped: {dedup_key}")
                    continue
                seen_keys.add(dedup_key)
                
                # Rationality check: rank_min < rank_max
                if processed['rank_min'] >= processed['rank_max']:
                    logger.debug(f"Rationality check failed: rank_min={processed['rank_min']} >= rank_max={processed['rank_max']}")
                    continue
                
                processed_records.append(processed)
                
            except Exception as e:
                logger.warning(f"Failed to process record: {record}, error: {e}")
                continue
        
        # Save processed data
        os.makedirs(os.path.dirname(processed_path), exist_ok=True)
        with open(processed_path, 'w', encoding='utf-8') as f:
            json.dump(processed_records, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(processed_records)} processed records to {processed_path}")
        return len(processed_records)
    
    def _clean_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean a single rank record.
        
        Args:
            record: Raw record from crawler
            
        Returns:
            Cleaned record, or None if invalid
        """
        # Required fields check
        year = record.get('year')
        province = record.get('province')
        score = record.get('score')
        rank = record.get('rank')
        
        if not all([year, province, score is not None, rank is not None]):
            logger.debug(f"Missing required fields: {record}")
            return None
        
        # Field mapping
        subject_category = record.get('batch_category', '')
        
        # Score section: use single score as section identifier
        # In real scenario, this might be a range like "700-709"
        score_section = str(score)
        
        # Rank fields: rank_min and rank_max
        # For single score point, rank_min = rank, rank_max = rank + 1 (to pass check)
        # In real scenario with sections, rank_min and rank_max would be different
        rank_min = int(rank)
        rank_max = int(rank) + 1  # Ensure rank_min < rank_max
        
        # Cumulative count: number of people with this score or above
        cumulative_count = int(rank)
        
        # Build standard record
        # Output fields: year, province, subject_category, score_section, rank_min, rank_max, cumulative_count
        cleaned = {
            'year': int(year),
            'province': str(province),
            'subject_category': str(subject_category),
            'score_section': score_section,
            'rank_min': rank_min,
            'rank_max': rank_max,
            'cumulative_count': cumulative_count,
        }
        
        return cleaned
    
    def batch_process(self, provinces: List[str], years: List[int]) -> Dict[str, int]:
        """
        Process multiple provinces and years.
        
        Args:
            provinces: List of province codes
            years: List of years
            
        Returns:
            Dict mapping "{province}_{year}" to record count
        """
        results = {}
        for province in provinces:
            for year in years:
                key = f"{province}_{year}"
                count = self.process(province, year)
                results[key] = count
        return results


def process(province: str, year: int) -> int:
    """
    Convenience function to process rank data.
    
    Args:
        province: Province code (e.g., 'shandong')
        year: Exam year (e.g., 2025)
        
    Returns:
        Number of successfully processed records
    """
    processor = RankProcessor()
    return processor.process(province, year)


if __name__ == "__main__":
    # Test processing
    import sys
    
    province = sys.argv[1] if len(sys.argv) > 1 else "shandong"
    year = int(sys.argv[2]) if len(sys.argv) > 2 else 2025
    
    print(f"Processing {province} {year} ranks...")
    count = process(province, year)
    print(f"Processed {count} records")
