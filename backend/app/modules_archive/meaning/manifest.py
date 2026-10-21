"""meaning 域声明（P7-B0 发现式加载）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "meaning",
    "title": "意义",
    "router_attr": "router",
    "frontend": {"path": "/meaning", "menu": "意义"},
    "cron": None,
}
