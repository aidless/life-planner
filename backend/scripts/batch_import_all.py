#!/usr/bin/env python3
"""
批量导入多省份PDF数据到数据库
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


def parse_jiangsu_pdf(pdf_path, subject_type):
    """解析江苏PDF（物理/历史类）"""
    records = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                for row in tables[0][3:]:  # 跳过前3行表头
                    if len(row) >= 3 and row[0] and row[1]:
                        college_code = row[0].strip()
                        college_major = row[1].strip()
                        min_score = row[2].strip()
                        
                        if not college_code or not college_major or "院校" in college_code:
                            continue
                        
                        # 解析院校名称和专业组
                        match = re.match(r'(.+?)(\d+专业组\([^)]+\))', college_major)
                        if match:
                            college_name = match.group(1).strip()
                            major_name = match.group(2).strip()
                        else:
                            college_name = college_major
                            major_name = ""
                        
                        min_score_clean = re.sub(r'[^\d]', '', min_score)
                        
                        records.append({
                            "college_name": college_name,
                            "major_name": f"{college_code} {major_name}" if major_name else college_code,
                            "min_score": int(min_score_clean) if min_score_clean else None,
                            "province": "江苏",
                            "year": 2025,
                            "subject_type": subject_type,
                            "batch": "本科批",
                            "source": f"jsjyksy_2025_{college_code}"
                        })
    
    return records


def parse_hubei_pdf(pdf_path, subject_type):
    """解析湖北PDF（物理/历史类）"""
    records = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                for row in tables[0][2:]:  # 跳过前2行表头
                    if len(row) >= 4 and row[0] and row[1]:
                        college_code = row[0].strip()
                        college_name = row[1].strip()
                        subject_req = row[2].strip() if len(row) > 2 else ""
                        min_score = row[3].strip() if len(row) > 3 else ""
                        
                        if not college_code or not college_name or "代号" in college_code:
                            continue
                        
                        min_score_clean = re.sub(r'[^\d]', '', min_score)
                        
                        records.append({
                            "college_name": college_name,
                            "major_name": f"{college_code} ({subject_req})",
                            "min_score": int(min_score_clean) if min_score_clean else None,
                            "province": "湖北",
                            "year": 2025,
                            "subject_type": subject_type,
                            "batch": "本科批",
                            "source": f"hbea_2025_{college_code}"
                        })
    
    return records


def parse_chongqing_pdf(pdf_path, subject_type):
    """解析重庆PDF（物理/历史类）"""
    records = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if tables:
                for row in tables[0][2:]:  # 跳过前2行表头
                    if len(row) >= 5 and row[0] and row[1]:
                        college_code = row[0].strip()
                        college_name = row[1].strip()
                        major_code = row[2].strip() if len(row) > 2 else ""
                        major_name = row[3].strip() if len(row) > 3 else ""
                        min_score = row[4].strip() if len(row) > 4 else ""
                        
                        if not college_code or not college_name or "代号" in college_code:
                            continue
                        
                        min_score_clean = re.sub(r'[^\d]', '', min_score)
                        
                        records.append({
                            "college_name": college_name,
                            "major_name": f"{major_code} {major_name}" if major_name else major_code,
                            "min_score": int(min_score_clean) if min_score_clean else None,
                            "province": "重庆",
                            "year": 2025,
                            "subject_type": subject_type,
                            "batch": "本科批",
                            "source": f"cqksy_2025_{college_code}"
                        })
    
    return records


async def import_records(records, province, subject_type):
    """导入记录到数据库"""
    async with AsyncSessionLocal() as session:
        # 删除现有数据
        result = await session.execute(
            select(CollegeScore).where(
                CollegeScore.province == province,
                CollegeScore.year == 2025,
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
        print(f"  导入完成: {len(records)} 条记录")


async def main():
    """主函数"""
    print("初始化数据库...")
    await init_db()
    
    # 定义要导入的文件
    files_to_import = [
        ("F:/life-planner/backend/data/raw/pdf/江苏_历史_2025.pdf", "江苏", "历史", parse_jiangsu_pdf),
        ("F:/life-planner/backend/data/raw/pdf/湖北_物理_2025.pdf", "湖北", "物理", parse_hubei_pdf),
        ("F:/life-planner/backend/data/raw/pdf/湖北_历史_2025.pdf", "湖北", "历史", parse_hubei_pdf),
        ("F:/life-planner/backend/data/raw/pdf/重庆_物理_2025.pdf", "重庆", "物理", parse_chongqing_pdf),
        ("F:/life-planner/backend/data/raw/pdf/重庆_历史_2025.pdf", "重庆", "历史", parse_chongqing_pdf),
    ]
    
    total_records = 0
    
    for filepath, province, subject_type, parse_func in files_to_import:
        if not filepath.endswith(".pdf"):
            continue
            
        print(f"\n处理: {province} {subject_type}")
        records = parse_func(filepath, subject_type)
        print(f"  提取 {len(records)} 条记录")
        
        if records:
            await import_records(records, province, subject_type)
            total_records += len(records)
    
    print(f"\n=== 总计导入 {total_records} 条记录 ===")


if __name__ == "__main__":
    asyncio.run(main())
