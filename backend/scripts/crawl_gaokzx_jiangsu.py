#!/usr/bin/env python3
"""
从gaokzx.com爬取江苏2025年投档线数据
"""

import json
from playwright.sync_api import sync_playwright


def crawl_jiangsu_2025():
    """爬取江苏2025年投档数据"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
            timezone_id="Asia/Shanghai"
        )
        
        page = context.new_page()
        
        try:
            # 访问江苏物理类投档线页面
            url = "https://www.gaokzx.com/gk/gaokao/144108.html"
            print(f"正在访问: {url}")
            page.goto(url, timeout=60000, wait_until="networkidle")
            page.wait_for_timeout(5000)
            
            # 截图
            page.screenshot(path="F:/life-planner/backend/scripts/jiangsu_physics_2025.png")
            print("已保存截图")
            
            # 获取页面标题和内容
            title = page.title()
            print(f"页面标题: {title}")
            
            body_text = page.inner_text("body")
            print(f"页面内容前2000字:\n{body_text[:2000]}")
            
            # 查找表格数据
            tables = page.query_selector_all("table")
            print(f"\n找到 {len(tables)} 个表格")
            
            # 提取第一个表格的数据
            if tables:
                table = tables[0]
                rows = table.query_selector_all("tr")
                print(f"第一个表格有 {len(rows)} 行")
                
                # 打印表头和前几行数据
                for i, row in enumerate(rows[:5]):
                    cells = row.query_selector_all("td, th")
                    cell_texts = [cell.inner_text().strip() for cell in cells]
                    print(f"  行 {i+1}: {cell_texts}")
            
            # 查找分页信息
            pagination = page.query_selector_all("[class*='page'], [class*='pagination']")
            print(f"\n找到 {len(pagination)} 个分页元素")
            
            # 保存HTML
            html = page.content()
            with open("F:/life-planner/backend/scripts/jiangsu_physics_2025.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("\n已保存HTML")
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()


if __name__ == "__main__":
    crawl_jiangsu_2025()
