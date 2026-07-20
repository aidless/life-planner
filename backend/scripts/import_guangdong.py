#!/usr/bin/env python3
"""
重新导入广东2024/2025年数据
"""

import json
import re
import asyncio
import sys
sys.path.append('F:/life-planner/backend')

import pdfplumber
from database import AsyncSessionLocal, init_db
from models.college_score import CollegeScore
from sqlalchemy import select


def clean_text(text):
    if text is None:
        return None
    return re.sub(r'\s+', ' ', text).strip()


def parse_guangdong_pdf(pdf_path, year, subject_type):
    """解析广东PDF"""
    records = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            
            for table in tables:
                if not table or len(table) < 2:
                    continue
                
                for row_idx, row in enumerate(table):
                    if row_idx == 0:
                        continue
                    
                    try:
                        if len(row) < 7:
                            continue
                        
                        college_code = clean_text(row[0])
                        college_name = clean_text(row[1])
                        
                        if not college_code or not college_name:
                            continue
                        
                        if '院校' in college_code or '代码' in college_code:
                            continue
                        
                        if not college_code.isdigit() or len(college_code) < 4:
                            continue
                        if '考' in college_name or '页' in college_name or '注' in college_name:
                            continue
                        
                        major_group_code = clean_text(row[2]) if len(row) > 2 else None
                        
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
                        
                        records.append({
                            "college_name": college_name,
                            "major_name": f"专业组{major_group_code}" if major_group_code else college_code,
                            "min_score": min_score,
                            "min_rank": min_rank,
                            "province": "广东",
                            "year": year,
                            "subject_type": subject_type,
                            "batch": "本科批",
                            "source": f"gdjyksy_{year}_{college_code}"
                        })
                    except Exception as e:
                        continue
    
    return records


async def import_records(records, province, year, subject_type):
    """导入记录"""
    async with AsyncSessionLocal() as session:
        # 删除现有数据
        result = await session.execute(
            select(CollegeScore).where(
                CollegeScore.province == province,
                CollegeScore.year == year,
                CollegeScore.subject_type == subject_type
            )
        )
        existing = result.scalars().all()
        
        if existing:
            for record in existing:
                await session.delete(record)
            await session.commit()
        
        # 导入新数据
        for i, record_data in enumerate(records):
            score = CollegeScore(**record_data)
            session.add(score)
            
            if (i + 1) % 100 == 0:
                await session.commit()
        
        await session.commit()
        print(f"  导入完成: {len(records)} 条")


async def main():
    print("初始化数据库...")
    await init_db()
    
    files = [
        ("F:/life-planner/backend/data/raw/pdf/guangdong_2024_physics.pdf", 2024, "物理"),
        ("F:/life-planner/backend/data/raw/pdf/guangdong_2024_history.pdf", 2024, "历史"),
        ("F:/life-planner/backend/data/raw/pdf/guangdong_2025_physics.pdf", 2025, "物理"),
        ("F:/life-planner/backend/data/raw/pdf/guangdong_2025_history.pdf", 2025, "历史"),
    ]
    
    total = 0
    for filepath, year, subject_type in files:
        print(f"\n处理: 广东 {year} {subject_type}")
        records = parse_guangdong_pdf(filepath, year, subject_type)
        print(f"  提取 {len(records)} 条记录")
        
        if records:
            await import_records(records, "广东", year, subject_type)
            total += len(records)
    
    print(f"\n=== 广东总计导入 {total} 条记录 ===")


if __name__ == "__main__":
    asyncio.run(main())
