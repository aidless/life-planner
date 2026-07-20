#!/usr/bin/env python3
"""
导入山东2024/2025年数据（XLS格式）
"""

import pandas as pd
import re
import asyncio
import sys
sys.path.append('F:/life-planner/backend')

from database import AsyncSessionLocal, init_db
from models.college_score import CollegeScore
from sqlalchemy import select


def parse_shandong_xls(filepath, year):
    """解析山东XLS"""
    # 读取Excel，不预设header
    df = pd.read_excel(filepath, header=None)
    
    # 自动检测数据起始行和列
    # 找到包含"专业代号"或"院校代号"的行作为表头
    header_row = None
    for idx, row in df.iterrows():
        row_str = ' '.join([str(x) for x in row if pd.notna(x)])
        if '专业代号' in row_str and '院校代号' in row_str:
            header_row = idx
            break
    
    if header_row is None:
        print(f"  未找到表头行")
        return []
    
    print(f"  表头在第 {header_row + 1} 行")
    
    # 找到有效数据列（非空列）
    data_columns = []
    for col in df.columns:
        if df.iloc[header_row, col] is not None and str(df.iloc[header_row, col]).strip() != '':
            data_columns.append(col)
    
    print(f"  有效数据列: {data_columns}")
    
    # 如果第一列是NaN，跳过它
    if len(data_columns) >= 4 and pd.isna(df.iloc[header_row + 1, data_columns[0]]):
        data_columns = data_columns[1:]
        print(f"  跳过空列后: {data_columns}")
    
    records = []
    
    # 从表头下一行开始读取数据
    for idx in range(header_row + 1, len(df)):
        row = df.iloc[idx]
        
        try:
            # 根据有效列数解析
            if len(data_columns) >= 4:
                major_info = str(row.iloc[data_columns[0]]).strip() if pd.notna(row.iloc[data_columns[0]]) else ""
                college_info = str(row.iloc[data_columns[1]]).strip() if pd.notna(row.iloc[data_columns[1]]) else ""
                plan_count = str(row.iloc[data_columns[2]]).strip() if pd.notna(row.iloc[data_columns[2]]) else ""
                min_rank_str = str(row.iloc[data_columns[3]]).strip() if pd.notna(row.iloc[data_columns[3]]) else ""
            elif len(data_columns) >= 3:
                major_info = str(row.iloc[data_columns[0]]).strip() if pd.notna(row.iloc[data_columns[0]]) else ""
                college_info = str(row.iloc[data_columns[1]]).strip() if pd.notna(row.iloc[data_columns[1]]) else ""
                min_rank_str = str(row.iloc[data_columns[2]]).strip() if pd.notna(row.iloc[data_columns[2]]) else ""
            else:
                continue
            
            if not major_info or not college_info:
                continue
            
            # 跳过表头行
            if "专业代号" in major_info or "院校代号" in college_info:
                continue
            
            # 解析院校信息
            college_match = re.match(r'([A-Z]?\d+)(.+)', college_info)
            if college_match:
                college_code = college_match.group(1)
                college_name = college_match.group(2).strip()
            else:
                college_code = ""
                college_name = college_info
            
            # 解析专业信息
            major_match = re.match(r'(\w+)(.+)', major_info)
            if major_match:
                major_code = major_match.group(1)
                major_name = major_match.group(2).strip()
            else:
                major_code = ""
                major_name = major_info
            
            # 解析最低位次
            min_rank = None
            rank_match = re.search(r'\d+', min_rank_str)
            if rank_match:
                min_rank = int(rank_match.group())
            
            records.append({
                "college_name": college_name,
                "major_name": f"{major_code} {major_name}" if major_code else major_name,
                "min_rank": min_rank,
                "province": "山东",
                "year": year,
                "subject_type": "综合",
                "batch": "常规批",
                "source": f"sdzk_{year}_{college_code}"
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
    
    # 导入2024年数据
    print("\n处理: 山东 2024")
    records = parse_shandong_xls("F:/life-planner/backend/data/raw/shandong_2024.xls", 2024)
    print(f"  提取 {len(records)} 条记录")
    
    if records:
        await import_records(records, "山东", 2024, "综合")
    
    # 导入2025年数据
    print("\n处理: 山东 2025")
    records = parse_shandong_xls("F:/life-planner/backend/data/raw/shandong_2025.xls", 2025)
    print(f"  提取 {len(records)} 条记录")
    
    if records:
        await import_records(records, "山东", 2025, "综合")


if __name__ == "__main__":
    asyncio.run(main())
