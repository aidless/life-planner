"""
Data quality monitors for Life Planner data pipeline.

Provides data quality checks and health report generation.
"""

import json
import os
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Expected record thresholds per province per year
# Format: {province_code: min_records}
EXPECTED_THRESHOLDS = {
    "shandong": 10000,
    "henan": 10000,
    "guangdong": 10000,
}

# Schema file paths
SCORE_SCHEMA_PATH = "data/schemas/score_schema.json"
RANK_SCHEMA_PATH = "data/schemas/rank_schema.json"

# Data directories
RAW_SCORES_DIR = "data/raw/scores"
RAW_RANKS_DIR = "data/raw/ranks"
PROCESSED_SCORES_DIR = "data/processed/scores"
PROCESSED_RANKS_DIR = "data/processed/ranks"
REPORTS_DIR = "data/quality/reports"


def check_freshness(province: Optional[str] = None, year: Optional[int] = None) -> Dict[str, Any]:
    """
    Check if province data is fresh (up-to-date with current year).
    
    Args:
        province: Province code to check (None for all)
        year: Year to check (None for current year)
        
    Returns:
        Dict with check results
    """
    from datetime import datetime as dt
    
    current_year = year or dt.now().year
    results = {
        "check_type": "freshness",
        "check_time": dt.now().isoformat(),
        "current_year": current_year,
        "provinces": {},
    }
    
    provinces_to_check = [province] if province else list(EXPECTED_THRESHOLDS.keys())
    
    for prov in provinces_to_check:
        province_result: Dict[str, Any] = {
            "status": "unknown",
            "details": [],
        }
        
        # Check raw scores
        raw_score_path = os.path.join(RAW_SCORES_DIR, f"{prov}_{current_year}.json")
        if os.path.exists(raw_score_path):
            mtime = os.path.getmtime(raw_score_path)
            mtime_dt = datetime.fromtimestamp(mtime)
            age_days = (dt.now() - mtime_dt).days
            
            if age_days <= 7:
                status = "✅"
                detail = f"Raw scores updated {age_days} days ago"
            elif age_days <= 30:
                status = "⚠️"
                detail = f"Raw scores updated {age_days} days ago (stale)"
            else:
                status = "❌"
                detail = f"Raw scores updated {age_days} days ago (very stale)"
            
            province_result["raw_scores"] = {
                "status": status,
                "detail": detail,
                "mtime": mtime_dt.isoformat(),
            }
        else:
            province_result["raw_scores"] = {
                "status": "❌",
                "detail": f"Raw scores file not found: {raw_score_path}",
            }
        
        # Check raw ranks
        raw_rank_path = os.path.join(RAW_RANKS_DIR, f"{prov}_ranks_{current_year}.json")
        if os.path.exists(raw_rank_path):
            mtime = os.path.getmtime(raw_rank_path)
            mtime_dt = datetime.fromtimestamp(mtime)
            age_days = (dt.now() - mtime_dt).days
            
            if age_days <= 7:
                status = "✅"
                detail = f"Raw ranks updated {age_days} days ago"
            elif age_days <= 30:
                status = "⚠️"
                detail = f"Raw ranks updated {age_days} days ago (stale)"
            else:
                status = "❌"
                detail = f"Raw ranks updated {age_days} days ago (very stale)"
            
            province_result["raw_ranks"] = {
                "status": status,
                "detail": detail,
                "mtime": mtime_dt.isoformat(),
            }
        else:
            province_result["raw_ranks"] = {
                "status": "❌",
                "detail": f"Raw ranks file not found: {raw_rank_path}",
            }
        
        # Determine overall status
        statuses = [v["status"] for v in province_result.values() if isinstance(v, dict) and "status" in v]
        if "❌" in statuses:
            province_result["status"] = "❌"
        elif "⚠️" in statuses:
            province_result["status"] = "⚠️"
        else:
            province_result["status"] = "✅"
        
        results["provinces"][prov] = province_result
    
    return results


def check_completeness(province: Optional[str] = None, year: Optional[int] = None) -> Dict[str, Any]:
    """
    Check if data record count meets expected thresholds.
    
    Args:
        province: Province code to check (None for all)
        year: Year to check (None for current year)
        
    Returns:
        Dict with check results
    """
    from datetime import datetime as dt
    
    current_year = year or dt.now().year
    results = {
        "check_type": "completeness",
        "check_time": dt.now().isoformat(),
        "year": current_year,
        "provinces": {},
    }
    
    provinces_to_check = [province] if province else list(EXPECTED_THRESHOLDS.keys())
    
    for prov in provinces_to_check:
        province_result = {
            "status": "unknown",
            "threshold": EXPECTED_THRESHOLDS.get(prov, 0),
            "scores": {},
            "ranks": {},
        }
        
        # Check processed scores count
        processed_score_path = os.path.join(PROCESSED_SCORES_DIR, f"{prov}_{current_year}.json")
        if os.path.exists(processed_score_path):
            with open(processed_score_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                count = len(data) if isinstance(data, list) else 0
            
            threshold = EXPECTED_THRESHOLDS.get(prov, 0)
            if count >= threshold:
                status = "✅"
                detail = f"Score records: {count} (threshold: {threshold})"
            elif count >= threshold * 0.5:
                status = "⚠️"
                detail = f"Score records: {count} (threshold: {threshold}, 50% met)"
            else:
                status = "❌"
                detail = f"Score records: {count} (threshold: {threshold}, insufficient)"
            
            province_result["scores"] = {
                "status": status,
                "count": count,
                "threshold": threshold,
                "detail": detail,
            }
        else:
            province_result["scores"] = {
                "status": "❌",
                "detail": f"Processed scores file not found: {processed_score_path}",
            }
        
        # Check processed ranks count
        processed_rank_path = os.path.join(PROCESSED_RANKS_DIR, f"{prov}_{current_year}.json")
        if not os.path.exists(processed_rank_path):
            # Try alternative naming
            processed_rank_path = os.path.join(PROCESSED_RANKS_DIR, f"{prov}_ranks_{current_year}.json")
        
        if os.path.exists(processed_rank_path):
            with open(processed_rank_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                count = len(data) if isinstance(data, list) else 0
            
            # Ranks typically have 550 records (750-200+1)
            rank_threshold = 550
            if count >= rank_threshold:
                status = "✅"
                detail = f"Rank records: {count} (expected: ~{rank_threshold})"
            elif count >= rank_threshold * 0.5:
                status = "⚠️"
                detail = f"Rank records: {count} (expected: ~{rank_threshold}, 50% met)"
            else:
                status = "❌"
                detail = f"Rank records: {count} (expected: ~{rank_threshold}, insufficient)"
            
            province_result["ranks"] = {
                "status": status,
                "count": count,
                "threshold": rank_threshold,
                "detail": detail,
            }
        else:
            province_result["ranks"] = {
                "status": "❌",
                "detail": f"Processed ranks file not found: {processed_rank_path}",
            }
        
        # Determine overall status
        statuses = []
        for key in ["scores", "ranks"]:
            if isinstance(province_result[key], dict) and "status" in province_result[key]:
                statuses.append(province_result[key]["status"])
        
        if "❌" in statuses:
            province_result["status"] = "❌"
        elif "⚠️" in statuses:
            province_result["status"] = "⚠️"
        else:
            province_result["status"] = "✅"
        
        results["provinces"][prov] = province_result
    
    return results


def check_schema_compliance(province: Optional[str] = None, year: Optional[int] = None, sample_size: int = 10) -> Dict[str, Any]:
    """
    Check if raw JSON files comply with schema.
    
    Args:
        province: Province code to check (None for all)
        year: Year to check (None for current year)
        sample_size: Number of records to sample for validation
        
    Returns:
        Dict with check results
    """
    from datetime import datetime as dt
    import jsonschema
    
    current_year = year or dt.now().year
    results = {
        "check_type": "schema_compliance",
        "check_time": dt.now().isoformat(),
        "year": current_year,
        "provinces": {},
    }
    
    provinces_to_check = [province] if province else list(EXPECTED_THRESHOLDS.keys())
    
    # Load schemas
    score_schema = None
    rank_schema = None
    
    if os.path.exists(SCORE_SCHEMA_PATH):
        with open(SCORE_SCHEMA_PATH, 'r', encoding='utf-8') as f:
            score_schema = json.load(f)
    
    if os.path.exists(RANK_SCHEMA_PATH):
        with open(RANK_SCHEMA_PATH, 'r', encoding='utf-8') as f:
            rank_schema = json.load(f)
    
    for prov in provinces_to_check:
        province_result = {
            "status": "unknown",
            "scores": {},
            "ranks": {},
        }
        
        # Check raw scores schema
        raw_score_path = os.path.join(RAW_SCORES_DIR, f"{prov}_{current_year}.json")
        if os.path.exists(raw_score_path) and score_schema:
            try:
                with open(raw_score_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    # Sample records for validation
                    sample = data[:sample_size] if len(data) > sample_size else data
                    valid_count = 0
                    errors = []
                    
                    for record in sample:
                        try:
                            jsonschema.validate(record, score_schema["items"])
                            valid_count += 1
                        except jsonschema.ValidationError as e:
                            errors.append(str(e.message))
                    
                    if valid_count == len(sample):
                        status = "✅"
                        detail = f"All {len(sample)} sampled records valid"
                    elif valid_count >= len(sample) * 0.8:
                        status = "⚠️"
                        detail = f"{valid_count}/{len(sample)} sampled records valid"
                    else:
                        status = "❌"
                        detail = f"Only {valid_count}/{len(sample)} sampled records valid"
                    
                    province_result["scores"] = {
                        "status": status,
                        "sampled": len(sample),
                        "valid": valid_count,
                        "errors": errors[:5],  # First 5 errors
                        "detail": detail,
                    }
                else:
                    province_result["scores"] = {
                        "status": "❌",
                        "detail": "Raw data is not a list",
                    }
            except Exception as e:
                province_result["scores"] = {
                    "status": "❌",
                    "detail": f"Schema validation error: {str(e)}",
                }
        elif not os.path.exists(raw_score_path):
            province_result["scores"] = {
                "status": "❌",
                "detail": f"Raw scores file not found: {raw_score_path}",
            }
        elif not score_schema:
            province_result["scores"] = {
                "status": "⚠️",
                "detail": f"Score schema not found: {SCORE_SCHEMA_PATH}",
            }
        
        # Check raw ranks schema
        raw_rank_path = os.path.join(RAW_RANKS_DIR, f"{prov}_ranks_{current_year}.json")
        if os.path.exists(raw_rank_path) and rank_schema:
            try:
                with open(raw_rank_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    # Sample records for validation
                    sample = data[:sample_size] if len(data) > sample_size else data
                    valid_count = 0
                    errors = []
                    
                    for record in sample:
                        try:
                            jsonschema.validate(record, rank_schema["items"])
                            valid_count += 1
                        except jsonschema.ValidationError as e:
                            errors.append(str(e.message))
                    
                    if valid_count == len(sample):
                        status = "✅"
                        detail = f"All {len(sample)} sampled records valid"
                    elif valid_count >= len(sample) * 0.8:
                        status = "⚠️"
                        detail = f"{valid_count}/{len(sample)} sampled records valid"
                    else:
                        status = "❌"
                        detail = f"Only {valid_count}/{len(sample)} sampled records valid"
                    
                    province_result["ranks"] = {
                        "status": status,
                        "sampled": len(sample),
                        "valid": valid_count,
                        "errors": errors[:5],
                        "detail": detail,
                    }
                else:
                    province_result["ranks"] = {
                        "status": "❌",
                        "detail": "Raw data is not a list",
                    }
            except Exception as e:
                province_result["ranks"] = {
                    "status": "❌",
                    "detail": f"Schema validation error: {str(e)}",
                }
        elif not os.path.exists(raw_rank_path):
            province_result["ranks"] = {
                "status": "❌",
                "detail": f"Raw ranks file not found: {raw_rank_path}",
            }
        elif not rank_schema:
            province_result["ranks"] = {
                "status": "⚠️",
                "detail": f"Rank schema not found: {RANK_SCHEMA_PATH}",
            }
        
        # Determine overall status
        statuses = []
        for key in ["scores", "ranks"]:
            if isinstance(province_result[key], dict) and "status" in province_result[key]:
                statuses.append(province_result[key]["status"])
        
        if "❌" in statuses:
            province_result["status"] = "❌"
        elif "⚠️" in statuses:
            province_result["status"] = "⚠️"
        else:
            province_result["status"] = "✅"
        
        results["provinces"][prov] = province_result
    
    return results


def generate_health_report(province: Optional[str] = None, year: Optional[int] = None, output_dir: str = REPORTS_DIR) -> str:
    """
    Generate Markdown health report.
    
    Args:
        province: Province code to check (None for all)
        year: Year to check (None for current year)
        output_dir: Directory to save report
        
    Returns:
        Path to generated report file
    """
    from datetime import datetime as dt
    
    # Run all checks
    freshness = check_freshness(province, year)
    completeness = check_completeness(province, year)
    schema = check_schema_compliance(province, year)
    
    # Generate Markdown report
    report_lines = []
    report_lines.append("# Data Quality Health Report")
    report_lines.append("")
    report_lines.append(f"**Check Time:** {dt.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"**Year:** {year or dt.now().year}")
    report_lines.append("")
    
    # Summary table
    report_lines.append("## Summary")
    report_lines.append("")
    report_lines.append("| Province | Freshness | Completeness | Schema | Overall |")
    report_lines.append("|----------|------------|--------------|--------|---------|")
    
    provinces = list(freshness["provinces"].keys())
    overall_status = {}
    
    for prov in provinces:
        f_status = freshness["provinces"][prov].get("status", "unknown")
        c_status = completeness["provinces"][prov].get("status", "unknown")
        s_status = schema["provinces"][prov].get("status", "unknown")
        
        # Determine overall
        statuses = [f_status, c_status, s_status]
        if "❌" in statuses:
            overall = "❌"
        elif "⚠️" in statuses:
            overall = "⚠️"
        else:
            overall = "✅"
        
        overall_status[prov] = overall
        
        report_lines.append(f"| {prov} | {f_status} | {c_status} | {s_status} | {overall} |")
    
    report_lines.append("")
    
    # Detailed sections
    report_lines.append("## Freshness Check Details")
    report_lines.append("")
    for prov, data in freshness["provinces"].items():
        report_lines.append(f"### {prov}")
        report_lines.append("")
        for key, val in data.items():
            if key == "status":
                continue
            if isinstance(val, dict):
                report_lines.append(f"- **{key}**: {val.get('detail', 'N/A')}")
        report_lines.append("")
    
    report_lines.append("## Completeness Check Details")
    report_lines.append("")
    for prov, data in completeness["provinces"].items():
        report_lines.append(f"### {prov}")
        report_lines.append("")
        for key, val in data.items():
            if key == "status":
                continue
            if isinstance(val, dict):
                report_lines.append(f"- **{key}**: {val.get('detail', 'N/A')}")
        report_lines.append("")
    
    report_lines.append("## Schema Compliance Check Details")
    report_lines.append("")
    for prov, data in schema["provinces"].items():
        report_lines.append(f"### {prov}")
        report_lines.append("")
        for key, val in data.items():
            if key == "status":
                continue
            if isinstance(val, dict):
                report_lines.append(f"- **{key}**: {val.get('detail', 'N/A')}")
                if val.get("errors"):
                    report_lines.append(f"  - Errors: {', '.join(val['errors'])}")
        report_lines.append("")
    
    # Save report
    os.makedirs(output_dir, exist_ok=True)
    report_filename = f"health_report_{dt.now().strftime('%Y%m%d_%H%M%S')}.md"
    report_path = os.path.join(output_dir, report_filename)
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))
    
    logger.info(f"Health report generated: {report_path}")
    return report_path


def main():
    """CLI entry point for monitors."""
    parser = argparse.ArgumentParser(description="Data quality monitors for Life Planner")
    parser.add_argument("--check", choices=["freshness", "completeness", "schema", "all"], default="all",
                        help="Type of check to run")
    parser.add_argument("--province", type=str, default=None,
                        help="Province code to check (default: all)")
    parser.add_argument("--year", type=int, default=None,
                        help="Year to check (default: current year)")
    parser.add_argument("--report", action="store_true",
                        help="Generate health report")
    
    args = parser.parse_args()
    
    if args.report or args.check == "all":
        # Generate health report
        report_path = generate_health_report(args.province, args.year)
        print(f"Health report generated: {report_path}")
    else:
        # Run specific check
        if args.check == "freshness":
            result = check_freshness(args.province, args.year)
        elif args.check == "completeness":
            result = check_completeness(args.province, args.year)
        elif args.check == "schema":
            result = check_schema_compliance(args.province, args.year)
        else:
            result = {}
        
        # Print result as JSON
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
