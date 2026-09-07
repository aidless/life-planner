"""dashboard 域声明（P7-B0 发现式加载）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "dashboard",
    "title": "仪表盘",
    "router_attr": "router",
    "frontend": {"path": "/dashboard", "menu": "仪表盘"},
    "cron": None,
}
