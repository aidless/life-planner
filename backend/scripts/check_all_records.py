#!/usr/bin/env python3
"""
检查所有记录，包括软删除的
"""

import asyncio
import sys
sys.path.append('F:/life-planner/backend')

from database import AsyncSessionLocal
from models.college_score import CollegeScore
from sqlalchemy import select, func


async def check_records():
    async with AsyncSessionLocal() as session:
        # 所有记录（包括软删除的）
        result = await session.execute(
            select(func.count()).select_from(CollegeScore)
        )
        total = result.scalar()
        print(f"总记录数（含软删除）: {total}")
        
        # 未删除的记录
        result = await session.execute(
            select(func.count()).select_from(CollegeScore).where(CollegeScore.is_deleted == False)
        )
        active = result.scalar()
        print(f"未删除记录数: {active}")
        
        # 已删除的记录
        result = await session.execute(
            select(func.count()).select_from(CollegeScore).where(CollegeScore.is_deleted == True)
        )
        deleted = result.scalar()
        print(f"已删除记录数: {deleted}")
        
        # 按省份统计所有记录
        result = await session.execute(
            select(CollegeScore.province, func.count())
            .group_by(CollegeScore.province)
            .order_by(func.count().desc())
        )
        provinces = result.all()
        print("\n按省份统计（所有记录）:")
        for province, count in provinces:
            print(f"  {province}: {count} 条")
        
        # 按年份统计
        result = await session.execute(
            select(CollegeScore.year, func.count())
            .group_by(CollegeScore.year)
            .order_by(CollegeScore.year)
        )
        years = result.all()
        print("\n按年份统计:")
        for year, count in years:
            print(f"  {year}: {count} 条")


if __name__ == "__main__":
    asyncio.run(check_records())
