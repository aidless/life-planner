#!/usr/bin/env python3
"""
解析江苏2025物理类PDF并导入数据库
"""

import json
import re
import asyncio
import sys
sys.path.append('F:/life-planner/backend')

from database import AsyncSessionLocal, init_db, engine
from models.college_score import CollegeScore
from sqlalchemy import select


def parse_jiangsu_pdf():
    """解析江苏PDF，返回结构化数据"""
    pdf_path = "F:/life-planner/backend/data/raw/pdf/jiangsu_2025_physics.pdf"
    
    import pdfplumber
    
    all_records = []
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"PDF总页数: {len(pdf.pages)}")
        
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            
            if tables:
                table = tables[0]
                
                # 跳过表头行（前3行），从第4行开始
                for row in table[3:]:
                    if len(row) >= 3 and row[0] and row[1]:
                        # 清理数据
                        college_code = row[0].strip() if row[0] else ""
                        college_major = row[1].strip() if row[1] else ""
                        min_score = row[2].strip() if row[2] else ""
                        
                        # 跳过无效行
                        if not college_code or not college_major or college_code == "院校":
                            continue
                        
                        # 解析院校名称和专业组
                        # 格式：院校名称XX专业组(再选科目要求)
                        match = re.match(r'(.+?)(\d+专业组\([^)]+\))', college_major)
                        if match:
                            college_name = match.group(1).strip()
                            major_name = match.group(2).strip()
                        else:
                            # 尝试其他格式
                            college_name = college_major
                            major_name = ""
                        
                        # 清理分数中的非数字字符
                        min_score_clean = re.sub(r'[^\d]', '', min_score)
                        
                        record = {
                            "college_name": college_name,
                            "major_name": f"{college_code} {major_name}" if major_name else college_code,
                            "min_score": int(min_score_clean) if min_score_clean else None,
                            "province": "江苏",
                            "year": 2025,
                            "subject_type": "物理",
                            "batch": "本科批",
                            "source": f"jsjyksy_2025_{college_code}"
                        }
                        
                        all_records.append(record)
            
            if (i + 1) % 10 == 0:
                print(f"已处理 {i+1}/{len(pdf.pages)} 页")
    
    print(f"共提取 {len(all_records)} 条记录")
    return all_records


async def import_to_database(records):
    """导入数据到数据库"""
    # 先初始化数据库表
    print("初始化数据库表...")
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # 检查现有数据
        result = await session.execute(
            select(CollegeScore).where(
                CollegeScore.province == "江苏",
                CollegeScore.year == 2025,
                CollegeScore.subject_type == "物理"
            )
        )
        existing = result.scalars().all()
        print(f"数据库中已有 {len(existing)} 条江苏2025物理类记录")
        
        # 如果已有数据，删除现有数据
        if existing:
            print("删除现有数据...")
            for record in existing:
                await session.delete(record)
            await session.commit()
        
        # 导入新数据
        print("导入新数据...")
        for i, record_data in enumerate(records):
            score = CollegeScore(**record_data)
            session.add(score)
            
            if (i + 1) % 100 == 0:
                await session.commit()
                print(f"已导入 {i+1}/{len(records)} 条记录")
        
        await session.commit()
        print(f"导入完成！共导入 {len(records)} 条记录")


if __name__ == "__main__":
    records = parse_jiangsu_pdf()
    
    # 保存为JSON供检查
    with open("F:/life-planner/backend/scripts/jiangsu_2025_physics.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    print("已保存JSON文件")
    
    # 导入数据库
    asyncio.run(import_to_database(records))
