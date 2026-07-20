#!/usr/bin/env python3
"""
详细检查山东2024年XLS文件结构
"""

import pandas as pd


def inspect_xls(filepath):
    """检查XLS结构"""
    df = pd.read_excel(filepath, header=None)
    
    print(f"总行数: {len(df)}")
    print(f"总列数: {len(df.columns)}")
    
    # 打印前20行，查看结构
    print(f"\n前20行数据（所有列）:")
    for idx in range(min(20, len(df))):
        row = df.iloc[idx]
        print(f"行 {idx}: {list(row)}")


if __name__ == "__main__":
    inspect_xls("F:/life-planner/backend/data/raw/shandong_2024.xls")
