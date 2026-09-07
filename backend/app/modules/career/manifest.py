"""career 域声明（P7-B0 发现式加载）。"""

from app.modules._manifest_schema import Manifest

MANIFEST: Manifest = {
    "name": "career",
    "title": "职业发展",
    "router_attr": "router",
    "frontend": {"path": "/career", "menu": "职业发展"},
    "cron": None,
}
