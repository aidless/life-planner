"""social 域声明（P7-B0 发现式加载）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "social",
    "title": "社交",
    "router_attr": "router",
    "frontend": {"path": "/social", "menu": "社交"},
    "cron": None,
}
