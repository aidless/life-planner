"""
Parse Guangdong 2025 physics PDF and extract admission score data.
"""

import pdfplumber
import json
import re
from pathlib import Path

PDF_PATH = "F:/life-planner/backend/data/raw/pdf/guangdong_2025_physics.pdf"
OUTPUT_PATH = "F:/life-planner/backend/data/raw/scores/guangdong_2025_physics.json"


def clean_text(text):
    """Remove extra whitespace and newlines."""
    if text is None:
        return None
    return re.sub(r'\s+', ' ', text).strip()


def parse_pdf(pdf_path: str) -> list:
    """Parse PDF and extract all table rows."""
    records = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            
            for table in tables:
                if not table or len(table) < 2:
                    continue
                
                # Find header row
                header = table[0]
                header_str = ' '.join(str(cell) for cell in header)
                if '院校代码' not in header_str:
                    continue  # Not the main table
                
                # Parse data rows
                for row_idx, row in enumerate(table[1:], start=2):
                    if not row or not row[0]:
                        continue
                    
                    # Filter: college_code should be digits only
                    college_code = str(row[0]).strip()
                    if not college_code.isdigit():
                        continue  # Skip non-data rows (headers, page numbers, etc.)
                    
                    # Filter: college_name should not start with page header markers
                    college_name = clean_text(row[1]) if len(row) > 1 else None
                    if college_name and (college_name.startswith('教 ') or college_name.startswith('省 ')):
                        continue  # Skip page header rows
                    
                    try:
                        # Safely parse numeric fields
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
                            "major_group_code": clean_text(row[2]) if len(row) > 2 else None,
                            "plan_count": plan_count,
                            "admit_count": admit_count,
                            "min_score": min_score,
                            "min_rank": min_rank,
                            "province": "广东",
                            "year": 2025,
                            "batch": "本科批",
                            "category": "物理类",
                        }
                        
                        records.append(record)
                    except Exception as e:
                        print(f"Error parsing row {row} on page {page_num + 1}: {e}")
                        continue
    
    return records


def main():
    print(f"Parsing {PDF_PATH} ...")
    records = parse_pdf(PDF_PATH)
    print(f"Extracted {len(records)} records")
    
    # Save to JSON
    output_path = Path(OUTPUT_PATH)
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
