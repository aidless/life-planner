#!/usr/bin/env python3
"""
检查PDF结构，用于了解不同省份的PDF格式
"""

import pdfplumber


def inspect_pdf(filepath, name):
    """检查PDF结构"""
    print(f"\n{'='*60}")
    print(f"检查: {name}")
    print(f"{'='*60}")
    
    with pdfplumber.open(filepath) as pdf:
        print(f"总页数: {len(pdf.pages)}")
        
        # 检查前3页
        for i in range(min(3, len(pdf.pages))):
            page = pdf.pages[i]
            print(f"\n--- 第 {i+1} 页 ---")
            
            # 提取文本
            text = page.extract_text()
            if text:
                print(f"文本前300字: {text[:300]}")
            
            # 提取表格
            tables = page.extract_tables()
            print(f"表格数量: {len(tables)}")
            
            if tables:
                table = tables[0]
                print(f"表格行数: {len(table)}")
                # 打印前5行
                for j, row in enumerate(table[:5]):
                    print(f"  行 {j+1}: {row}")


if __name__ == "__main__":
    files = [
        ("F:/life-planner/backend/data/raw/pdf/湖北_物理_2025.pdf", "湖北物理"),
        ("F:/life-planner/backend/data/raw/pdf/湖北_历史_2025.pdf", "湖北历史"),
        ("F:/life-planner/backend/data/raw/pdf/重庆_物理_2025.pdf", "重庆物理"),
        ("F:/life-planner/backend/data/raw/pdf/重庆_历史_2025.pdf", "重庆历史"),
        ("F:/life-planner/backend/data/raw/pdf/江苏_历史_2025.pdf", "江苏历史"),
    ]
    
    for filepath, name in files:
        inspect_pdf(filepath, name)
