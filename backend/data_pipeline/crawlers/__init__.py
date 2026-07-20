"""
Crawlers package for Life Planner data pipeline.

Contains web crawlers for collecting college admission data from various provinces.
"""

from .province_easy import (
    crawl_shandong_scores,
    crawl_henan_scores,
    crawl_guangdong_scores,
)

__all__ = [
    "crawl_shandong_scores",
    "crawl_henan_scores",
    "crawl_guangdong_scores",
]
