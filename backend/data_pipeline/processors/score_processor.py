"""
Score processor for Life Planner data pipeline.

Cleans raw score JSON from crawlers and converts to standard format
ready for bulk insert into CollegeScore model.
"""

import json
import os
import logging
from typing import List, Dict, Any, Set
from datetime import datetime

logger = logging.getLogger(__name__)

# Expected threshold for data completeness (records per province per year)
EXPECTED_MIN_RECORDS = {
    "shandong": 10000,
    "henan": 10000,
    "guangdong": 10000,
}


class ScoreProcessor:
    """
    Processor for college admission score data.
    
    Cleans raw crawler output and converts to standard format.
    """
    
    def __init__(self, raw_dir: str = "data/raw/scores", processed_dir: str = "data/processed/scores"):
        """
        Initialize processor.
        
        Args:
            raw_dir: Directory containing raw score JSON files
            processed_dir: Directory to save processed JSON files
        """
        self.raw_dir = raw_dir
        self.processed_dir = processed_dir
        os.makedirs(processed_dir, exist_ok=True)
    
    def process(self, province: str, year: int) -> int:
        """
        Process raw score data for a province and year.
        
        Args:
            province: Province code (e.g., 'shandong')
            year: Admission year (e.g., 2025)
            
        Returns:
            Number of successfully processed records
        """
        raw_path = os.path.join(self.raw_dir, f"{province}_{year}.json")
        processed_path = os.path.join(self.processed_dir, f"{province}_{year}.json")
        
        logger.info(f"Processing score data: {raw_path}")
        
        # Read raw data
        if not os.path.exists(raw_path):
            logger.error(f"Raw file not found: {raw_path}")
            return 0
        
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
                
                # Deduplication: same college+major+year+province
                dedup_key = f"{processed['college_name']}_{processed['major_name']}_{processed['year']}_{processed['province']}"
                if dedup_key in seen_keys:
                    logger.debug(f"Duplicate record skipped: {dedup_key}")
                    continue
                seen_keys.add(dedup_key)
                
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
        Clean a single score record.
        
        Args:
            record: Raw record from crawler
            
        Returns:
            Cleaned record, or None if invalid
        """
        # Field mapping: raw field names -> standard field names
        year = record.get('year')
        province = record.get('province')
        college_name = record.get('college_name')
        major_name = record.get('major_name')
        
        # Required fields check
        if not all([year, province, college_name, major_name]):
            logger.debug(f"Missing required fields: {record}")
            return None
        
        # Get score fields
        min_score = record.get('min_score')
        max_score = record.get('max_score')
        
        # Outlier filtering: score_min < 200 or > 750
        if min_score is not None:
            if isinstance(min_score, (int, float)):
                if min_score < 200 or min_score > 750:
                    logger.debug(f"Outlier score filtered: {min_score}")
                    return None
        
        # Type conversion: score_min to int
        score_min = None
        if min_score is not None:
            try:
                score_min = int(min_score)
            except (ValueError, TypeError):
                logger.debug(f"Invalid min_score: {min_score}")
                return None
        
        # Type conversion: score_max to int
        score_max = None
        if max_score is not None:
            try:
                score_max = int(max_score)
            except (ValueError, TypeError):
                logger.debug(f"Invalid max_score: {max_score}")
                # Don't return None, just leave as None
        
        # Build standard record
        # Output fields: year, province, college_name, major_name, batch, 
        #                score_min, score_max, plan_count, actual_count, tie_score, source_url
        cleaned = {
            'year': int(year),
            'province': str(province),
            'college_name': str(college_name),
            'major_name': str(major_name),
            'batch': record.get('batch'),
            'score_min': score_min,
            'score_max': score_max,
            'plan_count': record.get('plan_count'),  # Not in raw data, may be None
            'actual_count': record.get('actual_count'),  # Not in raw data, may be None
            'tie_score': bool(record.get('tie_score', False)),  # Default False
            'source_url': record.get('source', record.get('source_url', '')),
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
    Convenience function to process score data.
    
    Args:
        province: Province code (e.g., 'shandong')
        year: Admission year (e.g., 2025)
        
    Returns:
        Number of successfully processed records
    """
    processor = ScoreProcessor()
    return processor.process(province, year)


if __name__ == "__main__":
    # Test processing
    import sys
    
    province = sys.argv[1] if len(sys.argv) > 1 else "shandong"
    year = int(sys.argv[2]) if len(sys.argv) > 2 else 2025
    
    print(f"Processing {province} {year}...")
    count = process(province, year)
    print(f"Processed {count} records")
