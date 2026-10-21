"""intimacy 域声明（P7-B0 发现式加载）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "intimacy",
    "title": "亲密",
    "router_attr": "router",
    "frontend": {"path": "/intimacy", "menu": "亲密"},
    "cron": None,
}
