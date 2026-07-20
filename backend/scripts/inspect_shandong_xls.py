#!/usr/bin/env python3
"""
检查山东XLS文件结构
"""

import pandas as pd


def inspect_xls(filepath):
    """检查XLS结构"""
    # 读取Excel文件
    df = pd.read_excel(filepath)
    
    print(f"总行数: {len(df)}")
    print(f"\n列名: {list(df.columns)}")
    print(f"\n前5行数据:")
    print(df.head())
    print(f"\n数据类型:")
    print(df.dtypes)


if __name__ == "__main__":
    inspect_xls("F:/life-planner/backend/data/raw/shandong_2025.xls")
