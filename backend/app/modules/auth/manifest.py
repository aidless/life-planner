"""auth 域声明（P7-B0 发现式加载）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "auth",
    "title": "用户认证",
    "router_attr": "router",
    "frontend": None,
    "cron": None,
}
