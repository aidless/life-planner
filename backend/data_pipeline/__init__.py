"""
Data pipeline package for Life Planner application.

This package contains:
- crawlers/: Web crawlers for collecting college admission data
- processors/: Data processors for cleaning and transforming raw data
- scheduler.py: APScheduler configuration for periodic tasks (requires apscheduler package)
- monitors.py: Data quality monitoring and alerting
"""

# Note: Scheduler import is commented out because apscheduler is not installed
# from .scheduler import start_scheduler, stop_scheduler

__all__ = []  # ["start_scheduler", "stop_scheduler"]
