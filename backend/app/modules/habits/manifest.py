"""habits 域声明（P7-B0 发现式加载）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "habits",
    "title": "习惯",
    "router_attr": "router",
    "frontend": {"path": "/habits", "menu": "习惯"},
    "cron": None,
}
