#!/usr/bin/env python3
"""
尝试从河北省教育考试院爬取数据
"""

import json
from playwright.sync_api import sync_playwright


def crawl_hebei():
    """爬取河北高考数据"""
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
            timezone_id="Asia/Shanghai"
        )
        
        page = context.new_page()
        
        # 尝试多个可能的河北考试院网址
        urls = [
            "http://www.hebeea.edu.cn/",
            "https://www.hebeea.edu.cn/",
        ]
        
        for url in urls:
            try:
                print(f"正在访问: {url}")
                page.goto(url, timeout=30000, wait_until="networkidle")
                page.wait_for_timeout(3000)
                
                title = page.title()
                print(f"页面标题: {title}")
                
                body_text = page.inner_text("body")
                print(f"页面内容前500字: {body_text[:500]}")
                
                # 查找相关链接
                links = page.query_selector_all("a")
                print(f"找到 {len(links)} 个链接")
                
                for link in links[:10]:
                    text = link.inner_text().strip()
                    href = link.get_attribute("href")
                    if text and ("投档" in text or "分数线" in text or "录取" in text):
                        print(f"找到相关链接: {text} -> {href}")
                
                # 截图
                page.screenshot(path=f"F:/life-planner/backend/scripts/hebei_page_{url.split('//')[1].replace('/', '_')}.png")
                print("已保存截图")
                
            except Exception as e:
                print(f"访问 {url} 失败: {e}")
        
        browser.close()


if __name__ == "__main__":
    crawl_hebei()
