#!/usr/bin/env python3
"""
使用Playwright访问高考直通车，查找多省份历年投档数据
"""

import json
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


def crawl_from_gaokaozhitongche():
    """从高考直通车爬取数据"""
    
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
            print("正在访问高考直通车...")
            # 访问高考直通车官网
            page.goto("https://app.gaokaozhitongche.com/", timeout=60000, wait_until="networkidle")
            page.wait_for_timeout(3000)
            
            # 截图看看页面结构
            page.screenshot(path="F:/life-planner/backend/scripts/gaokaozhitongche_homepage.png")
            print("已保存首页截图")
            
            # 获取页面标题和内容
            title = page.title()
            print(f"页面标题: {title}")
            
            body_text = page.inner_text("body")
            print(f"页面内容前1000字: {body_text[:1000]}")
            
            # 查找所有链接
            links = page.query_selector_all("a")
            print(f"找到 {len(links)} 个链接")
            
            # 查找包含"投档"、"分数线"、"录取"等关键词的链接
            for i, link in enumerate(links):
                text = link.inner_text().strip()
                href = link.get_attribute("href")
                if text and ("投档" in text or "分数线" in text or "录取" in text or "数据" in text):
                    print(f"找到相关链接 {i+1}: {text} -> {href}")
            
            # 保存HTML
            html = page.content()
            with open("F:/life-planner/backend/scripts/gaokaozhitongche_homepage.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("已保存首页HTML")
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()


if __name__ == "__main__":
    crawl_from_gaokaozhitongche()
