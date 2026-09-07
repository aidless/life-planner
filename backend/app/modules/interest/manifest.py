"""interest 域声明（P7-B0 发现式加载）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "interest",
    "title": "兴趣",
    "router_attr": "router",
    "frontend": {"path": "/interest", "menu": "兴趣"},
    "cron": None,
}
