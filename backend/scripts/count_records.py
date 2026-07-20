#!/usr/bin/env python3
"""
统计数据库中的记录数
"""

import asyncio
import sys
sys.path.append('F:/life-planner/backend')

from database import AsyncSessionLocal
from models.college_score import CollegeScore
from sqlalchemy import select, func


async def count_records():
    async with AsyncSessionLocal() as session:
        # 总记录数
        result = await session.execute(select(func.count()).select_from(CollegeScore))
        total = result.scalar()
        print(f"总记录数: {total}")
        
        # 按省份统计
        result = await session.execute(
            select(CollegeScore.province, func.count()).group_by(CollegeScore.province)
        )
        provinces = result.all()
        print("\n按省份统计:")
        for province, count in sorted(provinces, key=lambda x: x[1], reverse=True):
            print(f"  {province}: {count} 条")
        
        # 按年份统计
        result = await session.execute(
            select(CollegeScore.year, func.count()).group_by(CollegeScore.year)
        )
        years = result.all()
        print("\n按年份统计:")
        for year, count in sorted(years, key=lambda x: x[0]):
            print(f"  {year}: {count} 条")
        
        # 按科类统计
        result = await session.execute(
            select(CollegeScore.subject_type, func.count()).group_by(CollegeScore.subject_type)
        )
        subjects = result.all()
        print("\n按科类统计:")
        for subject, count in sorted(subjects, key=lambda x: x[1], reverse=True):
            print(f"  {subject}: {count} 条")


if __name__ == "__main__":
    asyncio.run(count_records())
