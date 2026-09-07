"""daily_tracker 域声明（P7-B0 发现式加载）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "daily_tracker",
    "title": "日常记录",
    "router_attr": "router",
    "frontend": {"path": "/daily", "menu": "日常记录"},
    "cron": None,
}
