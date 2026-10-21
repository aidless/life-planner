"""travel 域声明（P7-B0 发现式加载）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "travel",
    "title": "旅行",
    "router_attr": "router",
    "frontend": {"path": "/travel", "menu": "旅行"},
    "cron": None,
}
