#!/usr/bin/env python3
"""
解析江苏省2025年普通高校招生普通类本科批次平行志愿投档线PDF
"""

import json
import pdfplumber


def parse_jiangsu_pdf():
    """解析江苏PDF"""
    pdf_path = "F:/life-planner/backend/data/raw/pdf/jiangsu_2025_physics.pdf"
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"PDF总页数: {len(pdf.pages)}")
        
        all_data = []
        
        # 解析前几页看看结构
        for i, page in enumerate(pdf.pages[:3]):
            print(f"\n=== 第 {i+1} 页 ===")
            
            # 提取文本
            text = page.extract_text()
            print(f"文本内容前500字:\n{text[:500] if text else '无文本'}")
            
            # 提取表格
            tables = page.extract_tables()
            print(f"找到 {len(tables)} 个表格")
            
            if tables:
                table = tables[0]
                print(f"表格行数: {len(table)}")
                
                # 打印表头和前几行
                for j, row in enumerate(table[:5]):
                    print(f"  行 {j+1}: {row}")
                
                # 将表格数据添加到all_data
                all_data.extend(table)
        
        # 保存解析的数据
        with open("F:/life-planner/backend/scripts/jiangsu_2025_physics_raw.json", "w", encoding="utf-8") as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        print(f"\n已保存原始数据，共 {len(all_data)} 行")


if __name__ == "__main__":
    parse_jiangsu_pdf()
