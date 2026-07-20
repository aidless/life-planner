#!/usr/bin/env python3
"""
访问高考直通车2025年专业录取分数线页面
"""

import json
from playwright.sync_api import sync_playwright


def crawl_2025_scores():
    """爬取2025年专业录取分数线"""
    
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
            print("正在访问2025年专业录取分数线页面...")
            page.goto("https://app.gaokaozhitongche.com/sharecd/2107332", timeout=60000, wait_until="networkidle")
            page.wait_for_timeout(5000)
            
            # 截图
            page.screenshot(path="F:/life-planner/backend/scripts/2025_scores_page.png")
            print("已保存页面截图")
            
            # 获取页面标题和内容
            title = page.title()
            print(f"页面标题: {title}")
            
            body_text = page.inner_text("body")
            print(f"页面内容前2000字:\n{body_text[:2000]}")
            
            # 查找表格数据
            tables = page.query_selector_all("table")
            print(f"\n找到 {len(tables)} 个表格")
            
            # 查找所有按钮和筛选器
            buttons = page.query_selector_all("button")
            print(f"找到 {len(buttons)} 个按钮")
            
            for i, btn in enumerate(buttons[:20]):
                text = btn.inner_text().strip()
                if text:
                    print(f"  按钮 {i+1}: {text}")
            
            # 查找省份选择器
            selectors = page.query_selector_all("select")
            print(f"\n找到 {len(selectors)} 个下拉选择框")
            
            # 查找输入框
            inputs = page.query_selector_all("input")
            print(f"找到 {len(inputs)} 个输入框")
            
            # 保存HTML
            html = page.content()
            with open("F:/life-planner/backend/scripts/2025_scores_page.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("\n已保存页面HTML")
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()


if __name__ == "__main__":
    crawl_2025_scores()
