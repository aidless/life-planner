"""family 域声明（P7-B0 发现式加载）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "family",
    "title": "家庭",
    "router_attr": "router",
    "frontend": {"path": "/family", "menu": "家庭"},
    "cron": None,
}
