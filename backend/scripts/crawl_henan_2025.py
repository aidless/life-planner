#!/usr/bin/env python3
"""
爬取河南省2025年普通高校招生投档分数线数据
使用Playwright浏览器自动化绕过JS渲染
"""

import json
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


def crawl_henan_2025():
    """爬取河南2025年投档数据"""
    
    with sync_playwright() as p:
        # 启动浏览器（非headless模式以便调试，但在这个环境中可能需要headless）
        browser = p.chromium.launch(headless=True)
        
        # 设置User-Agent和其他浏览器特征
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
            timezone_id="Asia/Shanghai"
        )
        
        page = context.new_page()
        
        try:
            print("正在访问河南省教育考试院官网...")
            # 使用HTTPS访问
            page.goto("https://www.haeea.cn/", timeout=60000, wait_until="networkidle")
            
            # 等待页面完全加载
            page.wait_for_timeout(5000)
            
            # 截图看看页面结构
            page.screenshot(path="F:/life-planner/backend/scripts/henan_homepage.png")
            print("已保存首页截图: henan_homepage.png")
            
            # 获取页面标题和内容
            title = page.title()
            print(f"页面标题: {title}")
            
            body_text = page.inner_text("body")
            print(f"页面内容长度: {len(body_text)}")
            print(f"页面内容前500字: {body_text[:500]}")
            
            # 查找所有链接
            links = page.query_selector_all("a")
            print(f"找到 {len(links)} 个链接")
            
            # 列出前20个链接的内容
            for i, link in enumerate(links[:20]):
                text = link.inner_text().strip()
                href = link.get_attribute("href")
                if text:
                    print(f"  链接 {i+1}: {text} -> {href}")
            
            # 查找2025年投档线相关链接
            target_link = None
            for link in links:
                text = link.inner_text().strip()
                href = link.get_attribute("href")
                
                # 查找包含关键词的链接
                if text and ("2025" in text or "投档" in text or "分数线" in text or "录取" in text):
                    print(f"找到相关链接: {text} -> {href}")
                    target_link = link
                    break
            
            if target_link:
                print(f"点击链接: {target_link.inner_text()}")
                target_link.click()
                page.wait_for_load_state("networkidle", timeout=60000)
                page.wait_for_timeout(3000)
                
                # 截图新页面
                page.screenshot(path="F:/life-planner/backend/scripts/henan_2025_page.png")
                print("已保存2025年页面截图: henan_2025_page.png")
                
                # 获取页面内容
                content = page.content()
                print(f"页面内容长度: {len(content)}")
                
                # 尝试提取表格数据
                tables = page.query_selector_all("table")
                print(f"找到 {len(tables)} 个表格")
                
                # 保存页面HTML供分析
                with open("F:/life-planner/backend/scripts/henan_2025_page.html", "w", encoding="utf-8") as f:
                    f.write(content)
                print("已保存页面HTML: henan_2025_page.html")
                
            else:
                print("未找到2025年投档数据相关链接")
                # 保存HTML以供分析
                html = page.content()
                with open("F:/life-planner/backend/scripts/henan_homepage.html", "w", encoding="utf-8") as f:
                    f.write(html)
                print("已保存首页HTML: henan_homepage.html")
            
        except PlaywrightTimeout as e:
            print(f"超时错误: {e}")
        except Exception as e:
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()


if __name__ == "__main__":
    crawl_henan_2025()
