"""college 域声明（P7-B0 发现式加载）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "college",
    "title": "高考志愿",
    "router_attr": "router",
    "frontend": {"path": "/college", "menu": "高考志愿"},
    "cron": None,
}
