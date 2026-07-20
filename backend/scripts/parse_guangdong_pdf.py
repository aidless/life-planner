"""
Parse Guangdong province college admission PDF and extract score data.
Usage: python parse_guangdong_pdf.py <input_pdf> <output_json> [--year YEAR] [--category CATEGORY]
"""

import pdfplumber
import json
import re
import sys
from pathlib import Path


def clean_text(text):
    """Remove extra whitespace and newlines."""
    if text is None:
        return None
    return re.sub(r'\s+', ' ', text).strip()


def parse_pdf(pdf_path: str, year: int = 2025, category: str = "物理类") -> list:
    """Parse PDF and extract all table rows."""
    records = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            
            for table in tables:
                if not table or len(table) < 2:
                    continue
                
                # Skip header rows
                for row_idx, row in enumerate(table):
                    if row_idx == 0:
                        continue  # Skip header
                    
                    try:
                        # Row format: [院校代码, 院校名称, 专业组代码, 计划数, 投档人数, 投档最低分, 投档最低排位]
                        if len(row) < 7:
                            continue
                        
                        college_code = clean_text(row[0])
                        college_name = clean_text(row[1])
                        
                        if not college_code or not college_name:
                            continue
                        
                        # Skip header/footer rows
                        if '院校' in college_code or '代码' in college_code:
                            continue
                        
                        # Skip invalid college names (parsing errors)
                        if not college_code.isdigit() or len(college_code) < 4:
                            continue
                        if '考' in college_name or '页' in college_name or '注' in college_name:
                            continue
                        
                        major_group_code = clean_text(row[2]) if len(row) > 2 else None
                        
                        plan_count = None
                        if len(row) > 3 and row[3] is not None:
                            match = re.search(r'\d+', str(row[3]))
                            if match:
                                plan_count = int(match.group())
                        
                        admit_count = None
                        if len(row) > 4 and row[4] is not None:
                            match = re.search(r'\d+', str(row[4]))
                            if match:
                                admit_count = int(match.group())
                        
                        min_score = None
                        if len(row) > 5 and row[5] is not None:
                            match = re.search(r'[\d.]+', str(row[5]))
                            if match:
                                min_score = float(match.group())
                        
                        min_rank = None
                        if len(row) > 6 and row[6] is not None:
                            match = re.search(r'\d+', str(row[6]))
                            if match:
                                min_rank = int(match.group())
                        
                        record = {
                            "college_code": college_code,
                            "college_name": college_name,
                            "major_group_code": major_group_code,
                            "plan_count": plan_count,
                            "admit_count": admit_count,
                            "min_score": min_score,
                            "min_rank": min_rank,
                            "province": "广东",
                            "year": year,
                            "batch": "本科批",
                            "category": category,
                        }
                        
                        records.append(record)
                    except Exception as e:
                        print(f"Error parsing row {row} on page {page_num + 1}: {e}")
                        continue
    
    return records


def main():
    if len(sys.argv) < 3:
        print("Usage: python parse_guangdong_pdf.py <input_pdf> <output_json> [--year YEAR] [--category CATEGORY]")
        sys.exit(1)
    
    input_pdf = sys.argv[1]
    output_json = sys.argv[2]
    
    # Parse optional args
    year = 2025
    category = "物理类"
    
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == '--year' and i + 1 < len(sys.argv):
            year = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == '--category' and i + 1 < len(sys.argv):
            category = sys.argv[i + 1]
            i += 2
        else:
            i += 1
    
    print(f"Parsing {input_pdf} ...")
    records = parse_pdf(input_pdf, year=year, category=category)
    print(f"Extracted {len(records)} records")
    
    # Save to JSON
    output_path = Path(output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    
    print(f"Saved to {output_path}")
    
    # Print sample
    if records:
        print("\nSample record:")
        print(json.dumps(records[0], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
