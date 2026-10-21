"""learning 域声明（P7-B0 发现式加载）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "learning",
    "title": "学习",
    "router_attr": "router",
    "frontend": {"path": "/learning", "menu": "学习"},
    "cron": None,
}
