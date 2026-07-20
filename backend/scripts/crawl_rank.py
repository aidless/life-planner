"""
CLI script to crawl rank data (一分一段表) for a specific province.

W29 fix: W3-era script referenced ``crawl_shandong_ranks`` which never
existed in ``data_pipeline/crawlers/province_easy.py``. We do not
introduce a placeholder — instead we use the existing
``crawl_shandong_scores`` to drive the pipeline, which produces the
rank table via the rank_processor.

Usage:
    python scripts/crawl_rank.py --province shandong
    python scripts/crawl_rank.py --province henan
    python scripts/crawl_rank.py --province guangdong
"""

import argparse
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# W29: Use the existing scores crawler; rank table is derived from it
from data_pipeline.crawlers.province_easy import crawl_shandong_scores
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for rank crawling script."""
    parser = argparse.ArgumentParser(description='Crawl rank data for a province')
    parser.add_argument(
        '--province',
        type=str,
        required=True,
        choices=['shandong', 'henan', 'guangdong'],
        help='Province to crawl (shandong/henan/guangdong)'
    )
    parser.add_argument(
        '--year',
        type=int,
        default=2025,
        help='Exam year (default: 2025)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='data/raw/scores',
        help='Output directory for raw data (default: data/raw/scores)'
    )

    args = parser.parse_args()

    # For MVP, only shandong has rank data implemented
    if args.province != 'shandong':
        logger.warning(f"Rank data crawling for {args.province} not yet implemented. Only shandong is available.")
        logger.info("Please implement crawl_{args.province}_ranks in data_pipeline/crawlers/province_easy.py")
        sys.exit(1)

    # Run crawler (only shandong for now). The rank table is then
    # derived from this score table by ``data_pipeline/processors/rank_processor``.
    try:
        output_path = crawl_shandong_scores(year=args.year, output_dir=args.output_dir)
        logger.info(f"✅ Crawling completed! Score data saved to: {output_path}")
        logger.info("Run the rank processor to derive the 一分一段表.")
        return 0
    except Exception as e:
        logger.error(f"❌ Crawling failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
