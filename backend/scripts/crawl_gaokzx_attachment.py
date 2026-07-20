#!/usr/bin/env python3
"""
从gaokzx.com查找并下载附件
"""

import json
import re
from playwright.sync_api import sync_playwright


def find_and_download_attachment():
    """查找并下载附件"""
    
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
            page.wait_for_timeout(3000)
            
            # 获取所有链接
            links = page.query_selector_all("a")
            print(f"\n找到 {len(links)} 个链接")
            
            # 查找附件链接（包含下载、附件、PDF、Excel等关键词）
            attachment_links = []
            for link in links:
                text = link.inner_text().strip()
                href = link.get_attribute("href")
                if href and ("download" in href.lower() or "附件" in text or "下载" in text or ".pdf" in href.lower() or ".xls" in href.lower() or ".xlsx" in href.lower() or ".doc" in href.lower() or ".zip" in href.lower()):
                    print(f"找到附件链接: {text} -> {href}")
                    attachment_links.append((text, href))
            
            # 查找包含"附件"文本的元素
            attachment_elements = page.query_selector_all("text=/附件|下载|PDF|Excel/")
            print(f"\n找到 {len(attachment_elements)} 个附件相关元素")
            for elem in attachment_elements[:10]:
                text = elem.inner_text().strip()
                print(f"  元素文本: {text}")
            
            # 获取页面HTML，用正则查找链接
            html = page.content()
            
            # 查找所有href链接
            href_pattern = r'href=["\']([^"\']+)["\']'
            all_hrefs = re.findall(href_pattern, html)
            print(f"\n正则找到 {len(all_hrefs)} 个href")
            
            for href in all_hrefs:
                if ".pdf" in href.lower() or ".xls" in href.lower() or ".xlsx" in href.lower() or ".doc" in href.lower() or ".zip" in href.lower() or "download" in href.lower():
                    print(f"  文件链接: {href}")
            
            # 保存HTML
            with open("F:/life-planner/backend/scripts/jiangsu_page_full.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("\n已保存完整HTML")
            
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()


if __name__ == "__main__":
    find_and_download_attachment()
