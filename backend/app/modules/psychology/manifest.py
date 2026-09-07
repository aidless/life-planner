"""psychology 域声明（P7-B0 发现式加载）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "psychology",
    "title": "心理",
    "router_attr": "router",
    "frontend": {"path": "/psychology", "menu": "心理"},
    "cron": None,
}
