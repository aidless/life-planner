"""
Try to download Guangdong 2024 admission PDFs.
"""
import requests
import re
import os

# Known URL patterns for Guangdong 2024
test_urls = [
    "https://eea.gd.gov.cn/eea/gkzy/2024/ptzy.html",
    "https://eea.gd.gov.cn/eea/gkzy/2024/index.html",
    "https://eea.gd.gov.cn/gkzy2024/ptzy.htm",
    "https://eea.gd.gov.cn/portal/index.html#/xgkzy/lnzslq/2024",
]

print("Testing Guangdong 2024 URL patterns...")
for url in test_urls:
    try:
        resp = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        content = resp.text.lower()
        has_pdf = "pdf" in content
        print(f"{url}: {resp.status_code}, len={len(resp.text)}, has_pdf={has_pdf}")
        if has_pdf and len(resp.text) < 200000:
            pdfs = re.findall(r'https?://[^\s"]+\.pdf', resp.text)
            if pdfs:
                print(f"  Found PDFs: {pdfs[:5]}")
    except Exception as e:
        print(f"{url}: ERROR {e}")

# Also try the known 2025 PDF URL pattern but with 2024
print("\nTrying known PDF URL patterns with 2024...")
known_patterns = [
    "https://eea.gd.gov.cn/attachments/2024/07/202407{day}_{seq}_tztz_{batch}.pdf",
]
# The 2025 PDFs were at: https://eea.gd.gov.cn/attachment/202507/20250717/20250717_4457141.pdf (physics)
# Let me try to guess 2024 patterns
for day in ["18", "19", "20", "21", "22"]:
    for batch in ["ptzy", "lszy"]:  # 普通志愿, 历史志愿
        url = f"https://eea.gd.gov.cn/attachment/202407/202407{day}/202407{day}_*_tztz_{batch}.pdf"
        print(f"Pattern: {url}")
        # Can't guess the exact filename, need to find index page
        break
    break

print("\nDone exploring.")
