#!/usr/bin/env python3
"""
访问河北省普通高考信息服务平台
"""

import json
from playwright.sync_api import sync_playwright


def crawl_hebei_gk():
    """爬取河北高考信息服务平台"""
    
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
            print("正在访问河北省普通高考信息服务平台...")
            page.goto("https://gk.hebeea.edu.cn/hebgk/", timeout=60000, wait_until="networkidle")
            page.wait_for_timeout(5000)
            
            # 截图
            page.screenshot(path="F:/life-planner/backend/scripts/hebei_gk_platform.png")
            print("已保存截图")
            
            # 获取页面标题和内容
            title = page.title()
            print(f"页面标题: {title}")
            
            body_text = page.inner_text("body")
            print(f"页面内容前1500字:\n{body_text[:1500]}")
            
            # 查找所有链接
            links = page.query_selector_all("a")
            print(f"\n找到 {len(links)} 个链接")
            
            # 查找投档、分数线、录取相关链接
            for link in links:
                text = link.inner_text().strip()
                href = link.get_attribute("href")
                if text and ("投档" in text or "分数线" in text or "录取" in text or "数据" in text or "查询" in text):
                    print(f"相关链接: {text} -> {href}")
            
            # 保存HTML
            html = page.content()
            with open("F:/life-planner/backend/scripts/hebei_gk_platform.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("\n已保存HTML")
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()


if __name__ == "__main__":
    crawl_hebei_gk()
