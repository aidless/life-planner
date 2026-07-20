#!/usr/bin/env python3
"""
批量爬取多省份2025年投档线PDF数据
"""

import json
import re
import os
from playwright.sync_api import sync_playwright

# 省份URL列表（从gaokzx.com）
PROVINCE_URLS = {
    "江苏_物理": "https://www.gaokzx.com/gk/gaokao/144108.html",
    "江苏_历史": "https://www.gaokzx.com/gk/gaokao/144110.html",
    "湖北_物理": "https://www.gaokzx.com/gk/zhiyuan/144756.html",
    "湖北_历史": "https://www.gaokzx.com/gk/zhiyuan/144758.html",
    "湖南_物理": "https://www.gaokzx.com/gk/zhiyuan/144469.html",
    "湖南_历史": "https://www.gaokzx.com/gk/zhiyuan/144470.html",
    "浙江": "https://www.gaokzx.com/gk/zhiyuan/144423.html",
    "安徽": "https://www.gaokzx.com/gk/gaokao/144514.html",
    "河北": "https://www.gaokzx.com/gk/zhiyuan/144397.html",
    "重庆_物理": "https://www.gaokzx.com/gk/zhiyuan/144434.html",
    "重庆_历史": "https://www.gaokzx.com/gk/zhiyuan/144431.html",
}


def extract_pdf_links():
    """从各省份页面提取PDF下载链接"""
    
    pdf_links = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
        )
        
        page = context.new_page()
        
        for province_name, url in PROVINCE_URLS.items():
            try:
                print(f"\n正在访问 {province_name}: {url}")
                page.goto(url, timeout=30000, wait_until="networkidle")
                page.wait_for_timeout(2000)
                
                # 查找PDF链接
                html = page.content()
                pdf_pattern = r'href=["\']([^"\']+\.pdf)["\']'
                pdf_matches = re.findall(pdf_pattern, html)
                
                if pdf_matches:
                    pdf_url = pdf_matches[0]
                    if not pdf_url.startswith("http"):
                        pdf_url = "https:" + pdf_url
                    pdf_links[province_name] = pdf_url
                    print(f"找到PDF: {pdf_url}")
                else:
                    print(f"未找到PDF链接")
                    
            except Exception as e:
                print(f"访问 {province_name} 失败: {e}")
        
        browser.close()
    
    # 保存链接
    with open("F:/life-planner/backend/scripts/province_pdf_links.json", "w", encoding="utf-8") as f:
        json.dump(pdf_links, f, ensure_ascii=False, indent=2)
    
    print(f"\n共找到 {len(pdf_links)} 个PDF链接")
    return pdf_links


def download_pdfs(pdf_links):
    """下载PDF文件"""
    import urllib.request
    
    download_dir = "F:/life-planner/backend/data/raw/pdf"
    os.makedirs(download_dir, exist_ok=True)
    
    downloaded = []
    
    for province_name, pdf_url in pdf_links.items():
        try:
            filename = f"{province_name.replace('/', '_')}_2025.pdf"
            filepath = os.path.join(download_dir, filename)
            
            print(f"\n下载 {province_name}: {pdf_url}")
            urllib.request.urlretrieve(pdf_url, filepath)
            
            file_size = os.path.getsize(filepath)
            print(f"下载完成: {filename} ({file_size/1024:.1f} KB)")
            downloaded.append((province_name, filepath))
            
        except Exception as e:
            print(f"下载 {province_name} 失败: {e}")
    
    return downloaded


if __name__ == "__main__":
    print("=== 第一步：提取PDF链接 ===")
    pdf_links = extract_pdf_links()
    
    print("\n=== 第二步：下载PDF文件 ===")
    downloaded = download_pdfs(pdf_links)
    
    print(f"\n共下载 {len(downloaded)} 个PDF文件")
