"""
Base crawler class for Life Planner data pipeline.

Provides common functionality for all crawlers:
- HTTP request with retry logic
- Rate limiting (delay between requests)
- Anti-bot detection avoidance
- Error handling and logging
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import random
import logging
from typing import Optional, Dict, Any


logger = logging.getLogger(__name__)

# User-Agent pool for rotation
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
]


class BaseCrawler:
    """
    Base crawler class with common crawling functionality.
    
    Features:
        - Session with retry logic
        - User-Agent rotation
        - Rate limiting
        - Error handling
    """
    
    def __init__(self, rate_limit: float = 3.0, max_retries: int = 3):
        """
        Initialize crawler.
        
        Args:
            rate_limit: Delay between requests in seconds (default: 3.0)
            max_retries: Maximum number of retry attempts (default: 3)
        """
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self.session = self._create_session()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def _get_headers(self) -> Dict[str, str]:
        """Generate random headers with User-Agent rotation."""
        return {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    def get(self, url: str, params: Optional[Dict] = None, **kwargs) -> requests.Response:
        """
        Make GET request with rate limiting and retry logic.
        
        Args:
            url: Target URL
            params: Query parameters
            **kwargs: Additional arguments for requests.get()
            
        Returns:
            Response object
            
        Raises:
            Exception: If all retries fail
        """
        # Rate limiting
        time.sleep(self.rate_limit + random.uniform(0, 1))
        
        headers = self._get_headers()
        kwargs.setdefault('headers', headers)
        kwargs.setdefault('timeout', 30)
        
        self.logger.info(f"GET {url}")
        
        try:
            response = self.session.get(url, params=params, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            self.logger.error(f"GET {url} failed: {e}")
            raise
    
    def post(self, url: str, data: Optional[Dict] = None, **kwargs) -> requests.Response:
        """
        Make POST request with rate limiting and retry logic.
        
        Args:
            url: Target URL
            data: POST data
            **kwargs: Additional arguments for requests.post()
            
        Returns:
            Response object
        """
        time.sleep(self.rate_limit + random.uniform(0, 1))
        
        headers = self._get_headers()
        kwargs.setdefault('headers', headers)
        kwargs.setdefault('timeout', 30)
        
        self.logger.info(f"POST {url}")
        
        try:
            response = self.session.post(url, data=data, **kwargs)
            response.raise_for_status()
            return response
        except Exception as e:
            self.logger.error(f"POST {url} failed: {e}")
            raise
    
    def save_raw_data(self, data: Any, filepath: str) -> None:
        """
        Save raw crawled data to file.
        
        Args:
            data: Data to save (will be converted to JSON)
            filepath: Output file path
        """
        import json
        import os
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"Saved raw data to {filepath}")
