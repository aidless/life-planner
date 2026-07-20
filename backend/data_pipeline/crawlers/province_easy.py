import json
import os
from datetime import datetime
from typing import List, Dict, Any
import logging
import pandas as pd
import requests

logger = logging.getLogger(__name__)


def crawl_shandong_scores(year: int = 2025, output_dir: str = "data/raw/scores", local_file: Optional[str] = None) -> str:
    """
    Crawl Shandong province college scores (REAL MODE).
    
    Fetches admission score data from Shandong exam bureau website,
    or reads from a local Excel file (for testing).
    
    Args:
        year: Admission year (e.g. 2025)
        output_dir: Output directory for processed data
        local_file: Path to local Excel file (for testing without web fetch)
    
    Returns:
        Path to generated JSON file
    """
    logger.info(f"Crawling Shandong province scores (year={year}, local_file={local_file})")
    
    # Step 1: Get Excel file (from web or local)
    excel_path = local_file
    if excel_path is None:
        excel_path = _fetch_shandong_excel(year)
        if excel_path is None:
            logger.error(f"Failed to fetch Shandong Excel for year {year}")
            return None
    
    # Step 2: Parse Excel file
    logger.info(f"Parsing Excel file: {excel_path}")
    # Shandong Excel has merged title row, so header is actually row 1 (0-indexed)
    # Read with header=None, then fix column names
    df_raw = pd.read_excel(excel_path, header=None, engine='xlrd' if excel_path.endswith('.xls') else 'openpyxl')
    
    # Find the real header row (contains "专业代号" or "院校代号")
    header_row_idx = None
    for idx, row in df_raw.iterrows():
        row_str = ' '.join([str(c) for c in row.values])
        if '专业代号' in row_str or '院校代号' in row_str:
            header_row_idx = idx
            break
    
    if header_row_idx is None:
        logger.error("Cannot find header row in Excel!")
        return None
    
    # Set column names from header row, data starts from header_row_idx+1
    df = df_raw.iloc[header_row_idx+1:].reset_index(drop=True)
    df.columns = df_raw.iloc[header_row_idx].values
    
    # Normalize column names (strip whitespace)
    df.columns = [str(c).strip() for c in df.columns]
    
    logger.info(f"Excel columns: {list(df.columns)}")
    logger.info(f"Excel shape: {df.shape}")
    logger.info(f"First 2 rows:\n{df.head(2).to_string()}")
    
    # Step 3: Transform to standard format
    records = []
    for _, row in df.iterrows():
        # Handle different column name variations
        # Shandong format: "院校代号及名称" (e.g. "A001北京大学")
        # Generic format: "院校名称" / "学校名称"
        college_name = _get_value(row, ['院校代号及名称', '院校名称', '学校名称', '院校', '学校'])
        major_name = _get_value(row, ['专业代号及名称', '专业名称', '专业'])
        batch = _get_value(row, ['批次', '录取批次'])
        min_score = _get_value(row, ['最低分', '投档最低分', '录取最低分', '分数线'])
        min_rank = _get_value(row, ['最低位次', '投档最低位次', '位次'])
        
        # Keep row if has college_name AND (min_score OR min_rank)
        if college_name is None or (min_score is None and min_rank is None):
            continue  # Skip invalid rows
            
        records.append({
            "year": year,
            "province": "山东",
            "college_name": _clean_name(str(college_name).strip()),
            "major_name": _clean_name(str(major_name).strip()) if major_name else None,
            "batch": str(batch).strip() if batch else "本科批",
            "min_score": _to_int(min_score),
            "min_rank": _to_int(min_rank),
            "source": f"sdzk.cn_{year}",
        })
    
    logger.info(f"Parsed {len(records)} valid records from Excel")
    
    # Step 4: Save to JSON
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"shandong_{year}.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved {len(records)} records to {output_path}")
    return output_path


def _fetch_shandong_excel(year: int) -> str:
    """
    Fetch the Excel file URL from Shandong exam bureau website, download it,
    and return the local file path.
    
    Returns:
        Local path to downloaded Excel file, or None if failed.
    """
    import re
    import os
    
    # Cache directory for downloaded Excel files
    cache_dir = "data/raw/excel"
    os.makedirs(cache_dir, exist_ok=True)
    cached_file = os.path.join(cache_dir, f"shandong_{year}.xls")
    
    # Check cache first
    if os.path.exists(cached_file):
        logger.info(f"Using cached Excel file: {cached_file}")
        return cached_file
    
    # Step 1: Try to find the detail page URL from known list pages
    detail_url = None
    
    # Known list page URLs to try (Shandong exam bureau)
    list_page_urls = [
        f"https://www.sdzk.cn/NewsList.aspx?BCID=12&CID=47",  # 招考热点
        f"https://www.sdzk.cn/NewsListM.aspx?BCID=2&CID=20",   # 夏季高考
    ]
    
    # Keywords to match in the link text
    keywords = f"{year}.*?普通类常规批第1次志愿投档情况表"
    
    for list_url in list_page_urls:
        try:
            resp = requests.get(list_url, timeout=15, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            resp.raise_for_status()
            html = resp.text
            
            # Find links matching the keywords
            # Pattern: match <a> tags where link text contains year + "普通类常规批第1次志愿投档情况表"
            # Use [^<] to prevent crossing tag boundaries
            pattern = rf'<a[^>]+href="(NewsInfo\.aspx\?NewsID=\d+[^"]*)"[^>]*>([^<]*?{year}[^<]*?普通类常规批第1次志愿投档情况表[^<]*)</a>'
            matches = re.findall(pattern, html)
            
            if matches:
                news_path = matches[0][0]  # First group is the href
                detail_url = f"https://www.sdzk.cn/{news_path}"
                logger.info(f"Found detail page: {detail_url}")
                break
                
        except Exception as e:
            logger.warning(f"Failed to fetch list page {list_url}: {e}")
            continue
    
    # Fallback: try known NewsID for specific years
    if detail_url is None:
        known_news_ids = {
            2025: "6996",  # 第1次志愿
            2024: "6656",  # 第1次志愿
        }
        if year in known_news_ids:
            detail_url = f"https://www.sdzk.cn/NewsInfo.aspx?NewsID={known_news_ids[year]}&BCID=20&a"
            logger.info(f"Using known detail page URL: {detail_url}")
        else:
            logger.error(f"Cannot find detail page for year {year}")
            return None
    
    # Step 2: Fetch the detail page to find Excel download link
    try:
        resp = requests.get(detail_url, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp.raise_for_status()
        html = resp.text
        
        # Find .xls or .xlsx download links
        # Pattern: href=".../...xls" or href=".../...xlsx"
        excel_pattern = r'href="([^"]*\.xls[x]?[^"]*)"'
        excel_matches = re.findall(excel_pattern, html, re.IGNORECASE)
        
        if not excel_matches:
            logger.error(f"No Excel download link found on detail page: {detail_url}")
            return None
        
        # Take the first Excel link
        excel_rel_path = excel_matches[0]
        # Convert relative URL to absolute
        if excel_rel_path.startswith('http'):
            excel_url = excel_rel_path
        elif excel_rel_path.startswith('/'):
            excel_url = f"https://www.sdzk.cn{excel_rel_path}"
        else:
            # Relative to the detail page's directory
            base = detail_url.rsplit('/', 1)[0]
            excel_url = f"{base}/{excel_rel_path}"
        
        # Clean up the URL (remove query params if any)
        excel_url = excel_url.split('?')[0]
        
        logger.info(f"Found Excel download URL: {excel_url}")
        
    except Exception as e:
        logger.error(f"Failed to parse detail page {detail_url}: {e}")
        return None
    
    # Step 3: Download the Excel file
    try:
        logger.info(f"Downloading Excel from {excel_url} ...")
        resp = requests.get(excel_url, timeout=60, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": detail_url,
        })
        resp.raise_for_status()
        
        # Save to cache
        with open(cached_file, 'wb') as f:
            f.write(resp.content)
        
        logger.info(f"Downloaded Excel file to {cached_file} (size: {len(resp.content)} bytes)")
        return cached_file
        
    except Exception as e:
        logger.error(f"Failed to download Excel file {excel_url}: {e}")
        return None


def crawl_henan_scores(year: int = 2025, output_dir: str = "data/raw/scores") -> str:
    """
    Crawl Henan province college scores (MOCK MODE).
    
    Args:
        year: Admission year
        output_dir: Output directory for raw data
    
    Returns:
        Path to generated JSON file
    """
    logger.info(f"Generating mock score data for Henan province (year={year})")
    
    mock_data = generate_mock_scores("河南", year)
    
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, f"henan_{year}.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(mock_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved {len(mock_data)} records to {output_path}")
    return output_path


def crawl_guangdong_scores(year: int = 2025, output_dir: str = "data/raw/scores") -> str:
    """
    Crawl Guangdong province college scores (MOCK MODE).
    
    Args:
        year: Admission year
        output_dir: Output directory for raw data
    
    Returns:
        Path to generated JSON file
    """
    logger.info(f"Generating mock score data for Guangdong province (year={year})")
    
    mock_data = generate_mock_scores("广东", year)
    
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, f"guangdong_{year}.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(mock_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"Saved {len(mock_data)} records to {output_path}")
    return output_path


def generate_mock_scores(province: str, year: int) -> List[Dict]:
    """Generate mock score data for testing."""
    colleges = [
        "清华大学", "北京大学", "复旦大学", "上海交通大学",
        "浙江大学", "中国科学技术大学", "南京大学", "武汉大学",
        "中山大学", "华南理工大学", "四川大学", "山东大学"
    ]
    
    majors = ["计算机科学与技术", "软件工程", "电子信息工程", "机械工程", "金融学"]
    
    data = []
    import random
    random.seed(42)
    
    for college in colleges:
        for major in majors:
            data.append({
                "year": year,
                "province": province,
                "college_name": college,
                "major_name": major,
                "batch": "本科批",
                "min_score": random.randint(580, 680),
                "min_rank": random.randint(1000, 15000),
                "source": "mock",
            })
    
    return data


def _get_value(row, possible_keys):
    """Get value from DataFrame row, trying multiple possible column names."""
    for key in possible_keys:
        for col in row.index:
            if key in str(col):
                val = row[col]
                if pd.notna(val):
                    return val
    return None


def _to_int(val):
    """Convert value to int, handling NaN/None."""
    import math
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def _clean_name(s: str) -> str:
    """Clean name by removing leading code prefix (e.g. 'A001北京大学' -> '北京大学')."""
    import re
    # Remove leading alphanumeric code (e.g. "A001", "17", "A001B")
    cleaned = re.sub(r'^[A-Za-z0-9]+', '', s).strip()
    # If regex didn't match (no code prefix), return original
    if cleaned == s:
        return s.strip()
    return cleaned
