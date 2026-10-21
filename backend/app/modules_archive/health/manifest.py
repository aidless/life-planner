"""health 域声明（P7-B0 试点）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "health",
    "title": "健康",
    "router_attr": "router",
    "frontend": {"path": "/health", "menu": "健康"},
    "cron": None,
}
