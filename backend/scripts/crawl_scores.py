"""
CLI script to crawl college score data for a specific province.

Usage:
    python scripts/crawl_scores.py --province shandong
    python scripts/crawl_scores.py --province henan
    python scripts/crawl_scores.py --province guangdong
"""

import argparse
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_pipeline.crawlers.province_easy import (
    crawl_shandong_scores,
    crawl_henan_scores,
    crawl_guangdong_scores,
)
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Province to crawler function mapping
PROVINCE_CRAWLERS = {
    'shandong': crawl_shandong_scores,
    'henan': crawl_henan_scores,
    'guangdong': crawl_guangdong_scores,
}


def main():
    """Main entry point for score crawling script."""
    parser = argparse.ArgumentParser(description='Crawl college score data for a province')
    parser.add_argument(
        '--province',
        type=str,
        required=True,
        choices=list(PROVINCE_CRAWLERS.keys()),
        help='Province to crawl (shandong/henan/guangdong)'
    )
    parser.add_argument(
        '--year',
        type=int,
        default=2025,
        help='Admission year (default: 2025)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/raw/scores',
        help='Output directory for raw data (default: data/raw/scores)'
    )
    
    args = parser.parse_args()
    
    # Get crawler function
    crawler_func = PROVINCE_CRAWLERS.get(args.province)
    if not crawler_func:
        logger.error(f"Unknown province: {args.province}")
        sys.exit(1)
    
    # Run crawler
    try:
        output_path = crawler_func(year=args.year, output_dir=args.output_dir)
        logger.info(f"✅ Crawling completed! Data saved to: {output_path}")
        return 0
    except Exception as e:
        logger.error(f"❌ Crawling failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
