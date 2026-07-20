#!/usr/bin/env python3
"""
深入查找河北省教育考试院的投档数据
"""

import json
from playwright.sync_api import sync_playwright


def crawl_hebei_detail():
    """深入爬取河北高考数据"""
    
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
            print("正在访问河北省教育考试院...")
            page.goto("http://www.hebeea.edu.cn/", timeout=30000, wait_until="networkidle")
            page.wait_for_timeout(3000)
            
            # 获取所有链接
            links = page.query_selector_all("a")
            print(f"找到 {len(links)} 个链接")
            
            # 查找包含"高考"、"投档"、"分数线"、"录取"、"信息"等关键词的链接
            target_urls = []
            for link in links:
                text = link.inner_text().strip()
                href = link.get_attribute("href")
                if text and ("高考" in text or "投档" in text or "分数线" in text or "录取" in text or "信息" in text):
                    print(f"相关链接: {text} -> {href}")
                    if href and href.startswith("http"):
                        target_urls.append((text, href))
            
            # 尝试点击"普通高考信息服务"
            for link in links:
                text = link.inner_text().strip()
                if "普通高考" in text or "信息服务" in text:
                    print(f"\n点击链接: {text}")
                    link.click()
                    page.wait_for_load_state("networkidle", timeout=30000)
                    page.wait_for_timeout(3000)
                    
                    print(f"新页面标题: {page.title()}")
                    body_text = page.inner_text("body")
                    print(f"新页面内容前1000字: {body_text[:1000]}")
                    
                    # 截图
                    page.screenshot(path="F:/life-planner/backend/scripts/hebei_gaokao_info.png")
                    print("已保存截图")
                    
                    # 在新页面查找投档数据链接
                    new_links = page.query_selector_all("a")
                    for new_link in new_links:
                        new_text = new_link.inner_text().strip()
                        new_href = new_link.get_attribute("href")
                        if new_text and ("投档" in new_text or "分数线" in new_text or "录取" in new_text):
                            print(f"在新页面找到相关链接: {new_text} -> {new_href}")
                    
                    break
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()


if __name__ == "__main__":
    crawl_hebei_detail()
