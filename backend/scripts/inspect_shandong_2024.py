#!/usr/bin/env python3
"""
检查山东2024年XLS文件结构
"""

import pandas as pd


def inspect_xls(filepath):
    """检查XLS结构"""
    # 读取Excel文件，不跳过任何行
    df = pd.read_excel(filepath, header=None)
    
    print(f"总行数: {len(df)}")
    print(f"\n前10行数据:")
    print(df.head(10))
    print(f"\n数据类型:")
    print(df.dtypes)


if __name__ == "__main__":
    inspect_xls("F:/life-planner/backend/data/raw/shandong_2024.xls")
