#!/usr/bin/env python3
"""
访问高考直通车专业分数线查询页面
"""

import json
from playwright.sync_api import sync_playwright


def crawl_college_major_line():
    """爬取专业分数线数据"""
    
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
            print("正在访问专业分数线查询页面...")
            page.goto("https://app.gaokaozhitongche.com/college-major-line/", timeout=60000, wait_until="networkidle")
            page.wait_for_timeout(5000)
            
            # 截图
            page.screenshot(path="F:/life-planner/backend/scripts/college_major_line.png")
            print("已保存页面截图")
            
            # 获取页面标题和内容
            title = page.title()
            print(f"页面标题: {title}")
            
            body_text = page.inner_text("body")
            print(f"页面内容前2000字:\n{body_text[:2000]}")
            
            # 查找表格数据
            tables = page.query_selector_all("table")
            print(f"\n找到 {len(tables)} 个表格")
            
            # 查找所有交互元素
            buttons = page.query_selector_all("button, .btn, [role='button']")
            print(f"找到 {len(buttons)} 个按钮")
            
            # 查找省份选择
            province_selectors = page.query_selector_all("[class*='province'], [class*='city'], [placeholder*='省份']")
            print(f"找到 {len(province_selectors)} 个省份选择器")
            
            # 查找下拉框
            selects = page.query_selector_all("select")
            print(f"找到 {len(selects)} 个下拉框")
            
            # 查找输入框
            inputs = page.query_selector_all("input")
            print(f"找到 {len(inputs)} 个输入框")
            
            # 保存HTML
            html = page.content()
            with open("F:/life-planner/backend/scripts/college_major_line.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("\n已保存页面HTML")
            
            # 尝试点击省份选择
            # 查找包含"广东"、"河南"等的元素
            province_elements = page.query_selector_all("text=/广东|河南|山东|河北|湖南|四川/")
            print(f"\n找到 {len(province_elements)} 个省份元素")
            for elem in province_elements[:10]:
                text = elem.inner_text().strip()
                print(f"  省份元素: {text}")
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()


if __name__ == "__main__":
    crawl_college_major_line()
